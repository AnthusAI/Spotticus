"""Steps for the SDK dispatch spec.

The probe and the scoring code are the real ones: the spec puts a stub `codexbar` on PATH
and lets spotticus parse and score its output. Only two things are faked - the leftover
numbers that stub reports, and the Claude Agent SDK itself, which is injected as a module
earlier on PYTHONPATH so no tokens are spent.

HOME is redirected into the scenario's temp directory, so the lock this spec claims is
never the real ~/.spotticus/locks/claude.default.json.
"""

import json
import os
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone

from behave import given, when, then

SDK_TRIGGER = os.path.abspath("scripts/trigger_claude_sdk.py")
REAL_SPOTTICUS = os.path.abspath(".venv/bin/spotticus")
VENV_PYTHON = os.path.abspath(".venv/bin/python")
SDK_TARGET = "claude.default"

FAKE_SDK = '''
"""Stand-in for claude-agent-sdk. Records the call; never talks to a model."""
import asyncio
import json
import os
from dataclasses import dataclass, field


class ClaudeAgentOptions:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class TextBlock:
    text: str


@dataclass
class ToolUseBlock:
    name: str
    id: str = "tool_1"
    input: dict = field(default_factory=dict)


@dataclass
class AssistantMessage:
    content: list


@dataclass
class ResultMessage:
    result: str = "chore complete"
    is_error: bool = False
    num_turns: int = 2
    total_cost_usd: float = 0.0


async def query(*, prompt, options=None, transport=None):
    with open(os.environ["SPEC_SDK_CALL"], "w") as f:
        json.dump({
            "prompt": prompt,
            "options": {k: repr(v) for k, v in vars(options).items()} if options else {},
        }, f)

    task_id = os.environ.get("SPEC_TASK_ID", "")
    task_file = os.environ.get("SPOTTICUS_TASK_FILE", "")
    if task_id and task_file:
        with open(task_file, "w") as f:
            f.write(task_id + "\\n")

    mode = os.environ.get("SPEC_SDK_MODE", "ok")
    if mode == "error":
        raise RuntimeError("spec forced SDK failure")

    if mode == "stream":
        for i in range(200):
            yield AssistantMessage(content=[TextBlock(text=f"working {i}")])
            await asyncio.sleep(0.2)

    yield AssistantMessage(content=[ToolUseBlock(name="Bash")])
    yield AssistantMessage(content=[TextBlock(text="did the chore")])
    yield ResultMessage()
'''

# Numbers the stub codexbar reports. "Spare" means well behind linear pace on both windows.
CODEXBAR_TEMPLATE = '''#!/bin/bash
cat <<'JSON'
{payload}
JSON
'''


def _usage_payload(used_primary, used_secondary):
    # CodexBar's claude provider reports its windows as top-level `primary`/`secondary`
    # dicts under `usage` (see tests/fixtures/codexbar_claude.json and the parser's claude
    # branch in spotticus/probes/codexbar.py). An earlier draft of this stub used a
    # `rateLimits` array, which the parser does not read, so the probe saw no windows and
    # every spare-pool scenario stood down before dispatch.
    now = datetime.now(timezone.utc)
    return json.dumps([{
        "provider": "claude",
        "source": "claude",
        "usage": {
            "updatedAt": now.isoformat().replace("+00:00", "Z"),
            "primary": {
                "usedPercent": used_primary,
                "windowMinutes": 300,
                "resetsAt": (now + timedelta(minutes=60)).isoformat().replace("+00:00", "Z"),
                "resetDescription": "spec primary",
            },
            "secondary": {
                "usedPercent": used_secondary,
                "windowMinutes": 10080,
                "resetsAt": (now + timedelta(minutes=2016)).isoformat().replace("+00:00", "Z"),
                "resetDescription": "spec secondary",
            },
        },
    }], indent=2)


def _sdk_setup(context):
    if hasattr(context, "sdk_dir"):
        return
    context.sdk_dir = tempfile.mkdtemp(prefix="spot-sdk-spec-")
    context.spec_dir = context.sdk_dir  # reuse the shared after_scenario cleanup
    context.sdk_home = os.path.join(context.sdk_dir, "home")
    context.sdk_bin = os.path.join(context.sdk_dir, "bin")
    context.sdk_lib = os.path.join(context.sdk_dir, "lib")
    for d in (context.sdk_home, context.sdk_bin, context.sdk_lib):
        os.makedirs(d, exist_ok=True)

    context.sdk_call = os.path.join(context.sdk_dir, "sdk_call.json")
    context.sdk_mode = "ok"
    context.spec_task_id = ""

    with open(os.path.join(context.sdk_lib, "claude_agent_sdk.py"), "w") as f:
        f.write(FAKE_SDK)


def _write_codexbar(context, payload=None, fail=False):
    path = os.path.join(context.sdk_bin, "codexbar")
    if fail:
        body = '#!/bin/bash\necho "spec forced probe failure" >&2\nexit 1\n'
    else:
        body = CODEXBAR_TEMPLATE.format(payload=payload)
    with open(path, "w") as f:
        f.write(body)
    os.chmod(path, 0o755)


def _sdk_lock_path(context):
    return os.path.join(context.sdk_home, ".spotticus", "locks", f"{SDK_TARGET}.json")


def _sdk_env(context):
    env = os.environ.copy()
    env.update({
        "HOME": context.sdk_home,
        "PATH": context.sdk_bin + os.pathsep + env.get("PATH", ""),
        "PYTHONPATH": context.sdk_lib + os.pathsep + env.get("PYTHONPATH", ""),
        "SPOTTICUS_TARGET": SDK_TARGET,
        "SPOT_MAX_TURNS": "7",
        "SPOT_MODEL": "claude-haiku-4-5",
        "SPOT_LOG_DIR": os.path.join(context.sdk_dir, "logs"),
        "SPEC_SDK_CALL": context.sdk_call,
        "SPEC_SDK_MODE": context.sdk_mode,
        "SPEC_TASK_ID": context.spec_task_id,
    })
    return env


def _spotticus(context, *args):
    return subprocess.run(
        [REAL_SPOTTICUS, *args], env=_sdk_env(context), capture_output=True, text=True
    )


@given(u'the leftover probe reports the claude pool is spare')
def step_impl(context):
    _sdk_setup(context)
    # 80% of the 5h window elapsed against 5% used, 80% of the week against 2% used.
    _write_codexbar(context, payload=_usage_payload(5, 2))


@given(u'the leftover probe reports the claude pool is at pace')
def step_impl(context):
    _sdk_setup(context)
    _write_codexbar(context, payload=_usage_payload(85, 82))


@given(u'the leftover probe fails for the claude pool')
def step_impl(context):
    _sdk_setup(context)
    _write_codexbar(context, fail=True)


@given(u'the claude pool is already locked by another agent')
def step_impl(context):
    res = _spotticus(
        context, "claim", SDK_TARGET, "--pid", str(os.getpid()),
        "--product", "Spec", "--model", "Spec", "--name", "OtherAgent",
    )
    assert res.returncode == 0, f"Could not seed the lock: {res.stderr}"


@given(u'the agent SDK will raise an error')
def step_impl(context):
    context.sdk_mode = "error"


@given(u'the agent SDK will keep streaming messages')
def step_impl(context):
    context.sdk_mode = "stream"


@when(u'the SDK spot trigger runs')
def step_impl(context):
    context.trigger = subprocess.run(
        [VENV_PYTHON, SDK_TRIGGER], env=_sdk_env(context),
        capture_output=True, text=True, timeout=120,
    )


@when(u'the SDK spot trigger runs and the pool is held')
def step_impl(context):
    proc = subprocess.Popen(
        [VENV_PYTHON, SDK_TRIGGER], env=_sdk_env(context),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    deadline = time.time() + 30
    while time.time() < deadline:
        if os.path.exists(context.sdk_call) and os.path.exists(_sdk_lock_path(context)):
            break
        time.sleep(0.2)
    else:
        proc.kill()
        raise AssertionError("Trigger never claimed the pool and started the agent")

    _spotticus(context, "hold", SDK_TARGET)
    out, err = proc.communicate(timeout=60)
    context.trigger = subprocess.CompletedProcess(proc.args, proc.returncode, out, err)


@then(u'the agent SDK is not called')
def step_impl(context):
    assert not os.path.exists(context.sdk_call), (
        f"The agent ran when it should not have: {context.trigger.stdout}"
    )
    assert context.trigger.returncode == 0, (
        f"Declining to dispatch is not an error: {context.trigger.stderr}"
    )
    assert context.trigger.stdout.strip(), "The trigger gave no reason for standing down"


@then(u'the agent SDK is called with permissions bypassed')
def step_impl(context):
    assert os.path.exists(context.sdk_call), (
        f"The agent was never run. stdout={context.trigger.stdout} stderr={context.trigger.stderr}"
    )
    with open(context.sdk_call) as f:
        context.sdk_payload = json.load(f)
    mode = context.sdk_payload["options"].get("permission_mode", "")
    assert "bypassPermissions" in mode, f"Permissions were not bypassed: {mode}"


@then(u'the run is capped by a turn ceiling')
def step_impl(context):
    turns = context.sdk_payload["options"].get("max_turns", "")
    assert turns == "7", f"The run was not capped at the configured turn ceiling: {turns!r}"


@then(u'the SDK worker prompt contains the Claude spot worker skill')
def step_impl(context):
    with open("skills/claude-spot-worker.md") as f:
        skill = f.read()
    marker = "## Workflow"
    assert marker in skill, "The skill has no Workflow section to hand the worker"
    assert marker in context.sdk_payload["prompt"], "The prompt does not carry the skill body"


@then(u'the SDK worker prompt leads with an instruction to begin')
def step_impl(context):
    opening = context.sdk_payload["prompt"].strip()[:400]
    assert not opening.startswith("---"), "The prompt opens with the skill's YAML frontmatter"
    assert "Begin immediately" in opening, (
        f"The prompt does not open by telling the worker to act: {opening[:200]}"
    )


@then(u'the run stops before the agent finishes')
def step_impl(context):
    assert "preempt" in context.trigger.stdout.lower(), (
        f"The trigger did not report stopping the run: {context.trigger.stdout}"
    )


@then(u'no lock remains for the claude pool')
def step_impl(context):
    assert not os.path.exists(_sdk_lock_path(context)), "The pool was left locked"


@then(u'the lock for the claude pool remains HELD')
def step_impl(context):
    assert os.path.exists(_sdk_lock_path(context)), "The on-demand hold was cleared by the trigger"
    again = subprocess.run(
        [VENV_PYTHON, SDK_TRIGGER], env=_sdk_env(context),
        capture_output=True, text=True, timeout=120,
    )
    assert "already claimed" in again.stdout, (
        f"A held pool accepted a new spot run: {again.stdout}"
    )
