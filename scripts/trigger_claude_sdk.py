#!/usr/bin/env python3
"""Spotticus dispatch, in-process, through the Claude Agent SDK.

scripts/trigger_claude.sh shells out to the Claude CLI and manages the worker with signals.
This path runs the same skill through claude-agent-sdk inside the Spotticus process, which
buys three things the CLI path cannot have:

  * max_turns - a real ceiling on agentic turns. The CLI has no such flag, which is why the
    shell trigger needs a wall-clock watchdog instead.
  * A message stream, so the run is logged as it happens and can be stopped between messages
    rather than only by killing a process.
  * In-process locking through spotticus.locks: no PID trap dance, and the runner can notice
    an on-demand hold itself.

The dispatch contract is identical to the shell trigger's, and it fails closed the same way:
a pool at pace, a probe error, or a pool already in use all mean no dispatch.
"""

from __future__ import annotations

import asyncio
import os
import signal
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from spotticus.locks import LockState, claim_lock, read_lock, release_lock  # noqa: E402
from spotticus.probes.codexbar import CodexBarProbe  # noqa: E402
from spotticus.scoring import score_provider  # noqa: E402

TARGET = os.environ.get("SPOTTICUS_TARGET", "claude.default")
THRESHOLD = float(os.environ.get("SPOT_THRESHOLD", "0.20"))
FLOOR = float(os.environ.get("SPOT_FLOOR", "15.0"))
MODEL = os.environ.get("SPOT_MODEL", "sonnet")
MAX_TURNS = int(os.environ.get("SPOT_MAX_TURNS", "60"))
AGENT_NAME = os.environ.get("SPOT_AGENT_NAME", "ClaudeSpotSdk")
SKILL_FILE = Path(os.environ.get("SKILL_FILE", REPO_ROOT / "skills" / "claude-spot-worker.md"))
LOG_DIR = Path(os.environ.get("SPOT_LOG_DIR", Path.home() / ".spotticus" / "logs"))

# Set by the SIGTERM handler. An on-demand hold preempts the *wrapper* (hold_lock SIGTERMs
# the pid it sees in the lock, which is this process), so without a handler the SDK trigger
# would die mid-stream before its preempted() poll could notice the lock flip to HELD. The
# handler just records the signal; the run_worker loop notices via preempted() and stops
# between messages, so the finally block can reopen the chore and report the preemption.
_PREEMPTED = False


def _on_term(signum, frame):  # noqa: ANN001
    global _PREEMPTED
    _PREEMPTED = True


def log(message: str) -> None:
    print(f"[trigger_claude_sdk] {message}", flush=True)


def build_prompt() -> str:
    """The skill body, led by the instruction to act on it.

    Order matters, and so does dropping the YAML frontmatter: handed the skill first, a
    worker reads the whole thing as documentation and asks whether it should begin.
    """
    lines = SKILL_FILE.read_text().splitlines()
    if lines and lines[0].strip() == "---":
        closing = next((i for i, ln in enumerate(lines[1:], start=1) if ln.strip() == "---"), 0)
        lines = lines[closing + 1:]
    body = "\n".join(lines).strip()

    return (
        f"You are the Spotticus spot worker for pool {TARGET}. You are running unattended: "
        "there is no human present and nobody will answer you. Begin immediately. Do not ask "
        "whether to start, do not summarise these instructions back, and do not wait for "
        "confirmation. Work exactly one Kanbus chore by the workflow below, then stop.\n\n"
        f"{body}\n\n"
        "Start now with step 1 of the workflow: find the work."
    )


def pool_is_spare() -> bool:
    """Probe and score in-process. Anything unreadable means no dispatch."""
    report = CodexBarProbe().probe(targets=[TARGET])
    if not report.results:
        log(f"No readable leftover for {TARGET}: {report.error}. Standing down.")
        return False

    provider, _, pool_id = TARGET.partition(".")
    now = datetime.now(timezone.utc)
    for result in report.results:
        if result.provider != provider:
            continue
        score = score_provider(result, now, spare_threshold=THRESHOLD, remaining_floor=FLOOR)
        pool = score.pool_scores.get(pool_id)
        if pool is None:
            continue
        if pool.is_eligible:
            return True
        windows_spare = bool(pool.window_scores) and all(w.is_spare for w in pool.window_scores)
        if windows_spare and pool.lock_data is not None:
            # The pool has spare quota but someone else holds the lock (a live spot run or
            # an on-demand HELD). Reporting "not spare" here would be misleading - the
            # capacity is there, the pool is just occupied - so say so and stand down.
            log(
                f"Pool {TARGET} is already claimed "
                f"(state {pool.lock_data.get('state', '?')}). Standing down."
            )
            return False
        log(f"{TARGET} is not spare (threshold {THRESHOLD}, floor {FLOOR}):")
        for window in pool.window_scores:
            log(
                f"  {window.window_name}: elapsed {window.elapsed_frac:.0%}, "
                f"used {window.used_frac:.0%}, spare {window.spare:+.2f}, "
                f"remaining {window.remaining_percent:.0f}%"
            )
        return False

    log(f"Probe returned nothing for {TARGET}. Standing down.")
    return False


def reopen_chore(task_file: Path, reason: str) -> None:
    """Hand an unfinished chore back to the queue rather than stranding it in progress."""
    if not task_file.exists():
        return
    task_id = task_file.read_text().strip()
    if not task_id:
        return
    log(f"Reopening Kanbus chore {task_id} ({reason}).")
    subprocess.run(["kbs", "update", task_id, "--status", "open"], capture_output=True, text=True)
    subprocess.run(
        [
            "kbs", "comment", task_id,
            f"Spot run on {TARGET} did not finish: {reason}. Reopened by trigger_claude_sdk.py.",
        ],
        capture_output=True, text=True,
    )


def preempted() -> bool:
    """True once this process no longer owns the pool - an on-demand hold took it."""
    if _PREEMPTED:
        return True
    lock = read_lock(TARGET)
    if lock is None:
        return True
    return lock.state != LockState.CLAIMED or lock.pid != os.getpid()


async def run_worker(prompt: str, log_file: Path) -> tuple[bool, str]:
    """Stream the agent, logging as it goes. Returns (finished_cleanly, reason)."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ClaudeAgentOptions as _Options,  # noqa: F401  (kept for readability below)
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        query,
    )

    options = ClaudeAgentOptions(
        model=MODEL,
        max_turns=MAX_TURNS,
        permission_mode="bypassPermissions",
        cwd=str(REPO_ROOT),
    )

    stream = query(prompt=prompt, options=options)
    with log_file.open("a") as out:
        try:
            async for message in stream:
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            out.write(f"{block.text}\n")
                        elif isinstance(block, ToolUseBlock):
                            out.write(f"[tool] {block.name}\n")
                        out.flush()
                elif isinstance(message, ResultMessage):
                    out.write(f"[result] {message.result}\n")
                    out.flush()
                    if getattr(message, "is_error", False):
                        return False, "the agent reported an error"

                if preempted():
                    return False, "preempted by an on-demand hold"
        finally:
            aclose = getattr(stream, "aclose", None)
            if aclose is not None:
                await aclose()

    return True, ""


def main() -> int:
    if not SKILL_FILE.is_file():
        log(f"Skill file {SKILL_FILE} is missing or unreadable.")
        return 1

    # An on-demand hold SIGTERMs the pid recorded in the lock (this process). Catch it so
    # the run_worker loop can stop between messages rather than being killed outright.
    signal.signal(signal.SIGTERM, _on_term)

    if not pool_is_spare():
        return 0
    log(f"Found spare capacity on {TARGET}.")

    if not claim_lock(
        target=TARGET, product="Claude Code", model=MODEL, name=AGENT_NAME, pid=os.getpid()
    ):
        log(f"Pool {TARGET} is already claimed. Standing down.")
        return 0
    log(f"Lock acquired for {TARGET}.")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"claude-spot-sdk-{datetime.now().strftime('%Y%m%dT%H%M%S')}.log"
    handle, task_path = tempfile.mkstemp(prefix="spot-claude-sdk-task")
    os.close(handle)
    task_file = Path(task_path)
    os.environ["SPOTTICUS_POOL"] = TARGET
    os.environ["SPOTTICUS_TASK_FILE"] = str(task_file)

    finished, reason = False, "the run did not complete"
    try:
        log(f"Running worker in-process (model {MODEL}, at most {MAX_TURNS} turns). Log: {log_file}")
        finished, reason = asyncio.run(run_worker(build_prompt(), log_file))
    except Exception as exc:  # noqa: BLE001 - any agent failure must still free the pool
        reason = f"the agent raised {type(exc).__name__}: {exc}"
        log(reason)
    finally:
        if finished:
            log("Worker finished.")
        else:
            log(f"Worker did not finish: {reason}")
            reopen_chore(task_file, reason)

        released, why = release_lock(target=TARGET, pid=os.getpid())
        if released:
            log(f"Released {TARGET}.")
        elif "HELD" in why:
            log(f"Pool {TARGET} is HELD by an on-demand hold; leaving the lock in place.")
        else:
            log(f"Could not release {TARGET}: {why}")
        task_file.unlink(missing_ok=True)

    return 0 if finished else 1


if __name__ == "__main__":
    sys.exit(main())
