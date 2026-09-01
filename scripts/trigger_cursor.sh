#!/bin/bash
# Cron wrapper for Cursor Composer Spot Dispatch
# Claims cursor.cursor-models and launches a headless Composer 2.5 agent.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

SPOTTICUS_CMD="${SPOTTICUS_CMD:-$REPO_ROOT/.venv/bin/spotticus}"
THRESHOLD="${SPOTTICUS_THRESHOLD:-0.20}"
TARGET="cursor.cursor-models"
AGENT_NAME="ComposerCron"
SKILL_PATH="$REPO_ROOT/skills/composer-spot-worker.md"

if ! command -v agent >/dev/null 2>&1; then
    echo "Cursor CLI (agent) is not on PATH. Fail closed; no dispatch."
    exit 0
fi

if [ ! -f "$SKILL_PATH" ]; then
    echo "Skill file missing: $SKILL_PATH. Fail closed; no dispatch."
    exit 0
fi

cursor_models_eligible() {
    "$SPOTTICUS_CMD" status --target "$TARGET" --threshold "$THRESHOLD" --json 2>/dev/null | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(1)
for provider in data.get("providers") or []:
    if provider.get("provider") != "cursor":
        continue
    pool = (provider.get("pools") or {}).get("cursor-models") or {}
    if pool.get("is_eligible"):
        sys.exit(0)
sys.exit(1)
'
}

if cursor_models_eligible; then
    echo "Found spare capacity in $TARGET"

    if $SPOTTICUS_CMD claim "$TARGET" --pid $$ --product Cursor --model "composer-2.5" --name "$AGENT_NAME"; then
        echo "Lock acquired. Launching Composer 2.5..."

        release_lock() {
            $SPOTTICUS_CMD release "$TARGET" --pid $$
        }
        trap release_lock EXIT

        PROMPT="$(cat "$SKILL_PATH")"
        # SPOTTICUS_POOL is the Kanbus label suffix (spot:cursor), not the lock target.
        SPOTTICUS_POOL=cursor agent -p "$PROMPT" --model composer-2.5 --trust --force --workspace "$REPO_ROOT"
        exit $?
    fi
fi

echo "No Cursor Models pool is currently eligible for spot dispatch."
