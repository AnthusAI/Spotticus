#!/usr/bin/env bash
# Cron wrapper for Claude Code spot dispatch.
#
# Probes the Claude pool for spare pace, claims the Spotticus lock, and runs a headless
# Claude Code agent against skills/claude-spot-worker.md for exactly one Kanbus chore.
#
# Fails closed: no readable leftover, a probe error, or a pool already in use means no
# dispatch. The lock is released on every exit path, and an on-demand hold preempts the
# worker and reopens its chore.
#
# Not "set -e": spotticus status exits 1 when nothing is eligible, which is a normal outcome.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1

SPOTTICUS_CMD="${SPOTTICUS_CMD:-$REPO_ROOT/.venv/bin/spotticus}"
CLAUDE_BIN="${CLAUDE_BIN:-claude}"
SKILL_FILE="${SKILL_FILE:-$REPO_ROOT/skills/claude-spot-worker.md}"
TARGET="${SPOTTICUS_TARGET:-claude.default}"
THRESHOLD="${SPOT_THRESHOLD:-0.20}"
FLOOR="${SPOT_FLOOR:-15.0}"
MODEL="${SPOT_MODEL:-sonnet}"
MAX_SECONDS="${SPOT_MAX_SECONDS:-2700}"
GRACE_SECONDS="${SPOT_GRACE_SECONDS:-10}"
AGENT_NAME="${SPOT_AGENT_NAME:-ClaudeSpotCron}"
LOG_DIR="${SPOT_LOG_DIR:-$HOME/.spotticus/logs}"

CLAUDE_PID=""
WATCHDOG_PID=""
RUN_STATUS=0
INTERRUPTED=0
TASK_FILE=""
TIMEOUT_MARKER=""

log() {
    echo "[trigger_claude] $*"
}

terminate_worker() {
    [ -n "$CLAUDE_PID" ] || return 0
    kill -0 "$CLAUDE_PID" 2>/dev/null || return 0
    kill -TERM "$CLAUDE_PID" 2>/dev/null
    local waited=0
    while kill -0 "$CLAUDE_PID" 2>/dev/null && [ "$waited" -lt "$GRACE_SECONDS" ]; do
        sleep 1
        waited=$((waited + 1))
    done
    kill -KILL "$CLAUDE_PID" 2>/dev/null
    return 0
}

# An on-demand hold SIGTERMs the claimed pid, which is this wrapper rather than the agent,
# so forward the signal on and let the normal exit path do the reopening and releasing.
on_term() {
    INTERRUPTED=1
    log "Preempted. Terminating the worker."
    terminate_worker
}

reopen_chore() {
    local task_id reason
    reason="$1"
    [ -n "$TASK_FILE" ] && [ -s "$TASK_FILE" ] || return 0
    task_id="$(tr -d '[:space:]' < "$TASK_FILE")"
    [ -n "$task_id" ] || return 0
    if ! command -v kbs >/dev/null 2>&1; then
        log "WARNING: kbs is not on PATH; chore $task_id is left in_progress ($reason)."
        return 0
    fi
    log "Reopening Kanbus chore $task_id ($reason)."
    if ! kbs update "$task_id" --status open >/dev/null 2>&1; then
        log "WARNING: could not reopen chore $task_id."
    fi
    kbs comment "$task_id" "Spot run on $TARGET did not finish: $reason. Reopened by trigger_claude.sh." >/dev/null 2>&1
    return 0
}

cleanup() {
    if [ -n "$WATCHDOG_PID" ]; then
        kill "$WATCHDOG_PID" 2>/dev/null
    fi
    terminate_worker

    if [ "$INTERRUPTED" -eq 1 ]; then
        reopen_chore "preempted by an on-demand hold"
    elif [ -n "$TIMEOUT_MARKER" ] && [ -s "$TIMEOUT_MARKER" ]; then
        reopen_chore "exceeded the ${MAX_SECONDS}s run cap"
    elif [ "$RUN_STATUS" -ne 0 ]; then
        reopen_chore "worker exited with status $RUN_STATUS"
    fi

    # A HELD lock belongs to whoever preempted us; refusing to release it is correct.
    local release_err
    release_err="$("$SPOTTICUS_CMD" release "$TARGET" --pid $$ 2>&1 >/dev/null)"
    if [ -n "$release_err" ]; then
        case "$release_err" in
            *HELD*) log "Pool $TARGET is HELD by an on-demand hold; leaving the lock in place." ;;
            *) log "Could not release $TARGET: $release_err" ;;
        esac
    else
        log "Released $TARGET."
    fi

    [ -n "$TASK_FILE" ] && rm -f "$TASK_FILE"
    [ -n "$TIMEOUT_MARKER" ] && rm -f "$TIMEOUT_MARKER"
    return 0
}

if [ ! -r "$SKILL_FILE" ]; then
    log "Skill file $SKILL_FILE is missing or unreadable."
    exit 1
fi

# 1. Probe. Anything other than an eligible pool means no dispatch.
STATUS_OUT="$("$SPOTTICUS_CMD" status --target "$TARGET" --threshold "$THRESHOLD" --floor "$FLOOR" 2>&1)"
if ! printf '%s' "$STATUS_OUT" | grep -q "ELIGIBLE"; then
    log "No dispatch on $TARGET (threshold $THRESHOLD, floor $FLOOR). Probe said:"
    printf '%s\n' "$STATUS_OUT" | sed 's/^/[trigger_claude]   /'
    exit 0
fi
log "Found spare capacity on $TARGET."

# 2. Claim the pool. One live spot run per pool.
if ! "$SPOTTICUS_CMD" claim "$TARGET" --pid $$ --product "Claude Code" --model "$MODEL" --name "$AGENT_NAME" >/dev/null 2>&1; then
    log "Pool $TARGET is already claimed. Standing down."
    exit 0
fi
log "Lock acquired for $TARGET."

# 3. From here on the lock is ours, so every exit path must give it back.
trap cleanup EXIT
trap on_term TERM INT

TASK_FILE="$(mktemp -t spot-claude-task)"
TIMEOUT_MARKER="$(mktemp -t spot-claude-timeout)"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/claude-spot-$(date +%Y%m%dT%H%M%S).log"

PROMPT="$(cat "$SKILL_FILE")

You are running now, unattended, on Spotticus pool $TARGET. Follow the workflow above for
exactly one Kanbus chore, then terminate."

# 4. Run the worker headless, capped by a watchdog: the CLI has no turn limit and this host
#    has no timeout(1), so a runaway agent would otherwise drain the whole window.
log "Launching headless worker (model $MODEL, cap ${MAX_SECONDS}s). Log: $LOG_FILE"
SPOTTICUS_POOL="$TARGET" SPOTTICUS_TASK_FILE="$TASK_FILE" \
    "$CLAUDE_BIN" -p "$PROMPT" \
    --dangerously-skip-permissions \
    --model "$MODEL" \
    --output-format text \
    >>"$LOG_FILE" 2>&1 &
CLAUDE_PID=$!

# Ticks rather than one long sleep so the watchdog goes away with the worker, and detaches
# its stdio so nothing downstream is left holding this script's pipes open.
(
    waited=0
    while [ "$waited" -lt "$MAX_SECONDS" ]; do
        kill -0 "$CLAUDE_PID" 2>/dev/null || exit 0
        sleep 1
        waited=$((waited + 1))
    done
    if kill -0 "$CLAUDE_PID" 2>/dev/null; then
        echo timeout > "$TIMEOUT_MARKER"
        kill -TERM "$CLAUDE_PID" 2>/dev/null
    fi
) >/dev/null 2>&1 &
WATCHDOG_PID=$!

wait "$CLAUDE_PID"
RUN_STATUS=$?
if [ "$INTERRUPTED" -eq 1 ]; then
    wait "$CLAUDE_PID" 2>/dev/null
    RUN_STATUS=143
fi

kill "$WATCHDOG_PID" 2>/dev/null
WATCHDOG_PID=""

if [ "$INTERRUPTED" -eq 1 ]; then
    log "Worker preempted."
elif [ -s "$TIMEOUT_MARKER" ]; then
    log "Worker exceeded the ${MAX_SECONDS}s cap and was terminated."
elif [ "$RUN_STATUS" -ne 0 ]; then
    log "Worker exited with status $RUN_STATUS. See $LOG_FILE."
else
    log "Worker finished."
fi

exit "$RUN_STATUS"
