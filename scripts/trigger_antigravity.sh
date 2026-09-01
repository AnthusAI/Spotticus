#!/bin/bash
# Cron wrapper for Antigravity Spot Dispatch
# This script explicitly filters for Antigravity's tracks.

# We lower the threshold to 0.10 for testing purposes
SPOTTICUS_CMD=".venv/bin/spotticus"
THRESHOLD="0.10"
AGENT_NAME="AntigravityCron"

# 1. Try the Gemini track first
if $SPOTTICUS_CMD status --target antigravity.gemini --threshold $THRESHOLD | grep -q "🟢 ELIGIBLE"; then
    echo "Found spare capacity in antigravity.gemini"
    
    # Claim the lock
    if $SPOTTICUS_CMD claim antigravity.gemini --pid $$ --product Antigravity --model "Gemini" --name "$AGENT_NAME"; then
        echo "Lock acquired. Launching Antigravity..."
        
        # Launch the agent with the specific skill
        # (In reality, this would be: SPOTTICUS_POOL=antigravity.gemini agy --skill skills/antigravity-spot-worker.md --model gemini-3.1-pro)
        echo "🤖 [Simulated AGY Invocation for antigravity.gemini]"
        
        # Release the lock when done
        $SPOTTICUS_CMD release antigravity.gemini --pid $$
        exit 0
    fi
fi

# 2. Fallback to the Claude/GPT track
if $SPOTTICUS_CMD status --target antigravity.claude --threshold $THRESHOLD | grep -q "🟢 ELIGIBLE"; then
    echo "Found spare capacity in antigravity.claude"
    
    if $SPOTTICUS_CMD claim antigravity.claude --pid $$ --product Antigravity --model "Claude" --name "$AGENT_NAME"; then
        echo "Lock acquired. Launching Antigravity..."
        
        # (In reality, this would be: SPOTTICUS_POOL=antigravity.claude agy --skill skills/antigravity-spot-worker.md --model claude-3.5-sonnet)
        echo "🤖 [Simulated AGY Invocation for antigravity.claude]"
        
        $SPOTTICUS_CMD release antigravity.claude --pid $$
        exit 0
    fi
fi

echo "No Antigravity pools are currently eligible for spot dispatch."
