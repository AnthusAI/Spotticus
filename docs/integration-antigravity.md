# Scheduling and Dispatch Integrations

Spotticus monitors your spare coding-agent quota and dispatches Kanbus chores when capacity is available. However, Spotticus needs a scheduler to run periodically.

This document covers how to schedule Spotticus specifically for **Google Antigravity**.

## The Authentication Pitfall (Why Cron Fails)

Your first instinct might be to schedule Spotticus using an OS-level `cron` job or a macOS `launchd` agent. **Do not do this.** 

OS-level background schedulers run in a sterile environment. They do not inherit your user session's authentication state, nor can they cleanly access the macOS Keychain where Antigravity stores its authentication tokens. If you use `cron` or `launchd` to invoke the Antigravity CLI (`agy`), it will instantly crash with an `authentication required` error.

**Rule:** The Spotticus polling daemon must be executed from within a fully authenticated environment.

---

## The Solution: Antigravity Sidecars

The officially supported and most robust way to run Spotticus is as an **Antigravity Sidecar**.

Sidecars are long-running background processes managed directly by the Antigravity desktop application. Because they are launched by Antigravity itself, they naturally inherit the exact same environment and authentication state as your interactive CLI and agents.

### 1. Create the Polling Daemon Script
Create a bash script (e.g., `~/run_spotticus_daemon.sh`) that acts as the bridge between Spotticus and the Antigravity CLI (`agy`):

```bash
#!/bin/bash
# Include cargo and local bin for kbs and agy, and Spotticus bin for probes
export PATH="~/Projects/Spotticus/bin:~/.cargo/bin:~/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "Starting Spotticus background daemon..."

while true; do
    cd ~/Projects/Spotticus
    SPARE_CAPACITY=$(.venv/bin/spotticus status --threshold=0.10)

    if echo "$SPARE_CAPACITY" | grep -q "🟢 ELIGIBLE"; then
        cd ~/Projects/YourProject
        OPEN_TASKS=$(kbs list --status open --label spot --porcelain)
        
        if [ -n "$OPEN_TASKS" ]; then
            FIRST_TASK_ID=$(echo "$OPEN_TASKS" | head -n 1 | awk -F'|' '{print $2}' | xargs)
            kbs update "$FIRST_TASK_ID" --status in_progress
            
            # Spawn the agent and block until it finishes. 
            # Note the 15m timeout to give it time to work!
            agy --dangerously-skip-permissions --print-timeout 15m --print "You are Spotticus executing a spot task. You must implement the requirements for Kanbus issue $FIRST_TASK_ID..."
        fi
    fi
    
    # Sleep for 5 minutes before polling again
    sleep 300
done
```
Make the script executable: `chmod +x ~/run_spotticus_daemon.sh`

### 2. Configure the Sidecar
Configure Antigravity to run this script as a Sidecar (refer to the Antigravity Sidecar documentation for the exact JSON schema). 

Once configured, whenever Antigravity is running on your machine, Spotticus will poll your quota and dispatch Kanbus chores flawlessly in the background without any authentication errors or token burn!
