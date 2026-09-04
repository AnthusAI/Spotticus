# Scheduling and Dispatch Integrations

Spotticus is responsible for monitoring your spare coding-agent quota and dispatching chores when capacity is available. However, Spotticus itself needs to be scheduled to run periodically to check this capacity.

This document covers the tradeoffs of different scheduling architectures and provides specific instructions for integrating with popular tools like **Google Antigravity**.

## The Architecture Tradeoff: Push vs. Pull

When integrating Spotticus with an agentic platform, you have two architectural choices:

### 1. The Push Model (Prompt-Based Scheduling)
In a Push model, you use the agent platform's native scheduling UI (e.g., Antigravity's `/schedule` or "Scheduled Tasks" sidebar). 
* **How it works:** The platform wakes up an LLM agent every `N` minutes with a text prompt like: *"Run Spotticus. If there's spare capacity, pick a Kanbus issue and write the code."*
* **Pros:** Extremely easy to set up using the platform's UI.
* **Cons (Critical):** **Token Burn.** This method wastes quota. The LLM must be invoked and fed context tokens every single time the schedule fires, just to realize that there is no spare capacity available. 
* **Verdict:** Avoid this model for high-frequency polling.

### 2. The Pull Model (Programmatic Cron) **(Recommended)**
In a Pull model, you decouple the capacity checking from the LLM execution. You use standard programmatic tools (like an OS `cron` job, a `systemd` timer, or an Antigravity Sidecar) to check for capacity, and only wake the LLM when there is actual work to do.
* **How it works:** 
  1. A local background job runs a lightweight shell script every 10-15 minutes.
  2. The script runs `spotticus status`. This CLI command evaluates Spotticus's nuanced heuristics locally (zero token cost)—calculating linear pace, checking absolute floors, and respecting holds, as detailed in [docs/dispatch.md](./dispatch.md).
  3. If capacity exists, it checks the Kanbus backlog for `spot` tasks (zero token cost).
  4. If both exist, it uses the platform's SDK (e.g., the Antigravity Python SDK or headless CLI) to programmatically spawn a sub-agent to do the work.
* **Pros:** Strictly preserves AI tokens for actual coding work.
* **Cons:** Requires a bit more initial setup in the terminal.

---

## Integration: Google Antigravity

To set up the optimal **Pull Model** with Google Antigravity, follow these steps:

### 1. Create the Dispatch Script
Create a bash script (e.g., `~/run_spotticus.sh`) that acts as the bridge between Spotticus and the Antigravity CLI (`agy`):

```bash
#!/bin/bash
# Include cargo and local bin for kbs and agy, and Spotticus bin for probes
export PATH="~/Projects/Spotticus/bin:~/.cargo/bin:~/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LOCKFILE="/tmp/spotticus.lock"
if [ -f "$LOCKFILE" ]; then
    exit 0
fi

touch "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

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
```
Make the script executable: `chmod +x ~/run_spotticus.sh`

### 2. Schedule the Script
**⚠️ macOS Warning: Do not use crontab!**
On macOS, `cron` runs in a restricted, headless environment and does not have access to the user's Keychain. Because Antigravity requires Keychain access to read authentication tokens, `agy` will instantly crash with an authentication error if run from `cron`.

Instead, use **launchd**, which runs inside the user's GUI session:

1. Create a plist file at `~/Library/LaunchAgents/com.spotticus.agent.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.spotticus.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/home/run_spotticus.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer> <!-- 5 minutes -->
</dict>
</plist>
```
2. Load the agent: `launchctl load ~/Library/LaunchAgents/com.spotticus.agent.plist`

### 3. Alternative: Antigravity Sidecars
If you prefer to manage the lifecycle of the daemon entirely within Antigravity without touching OS files, you can configure the bash script as an **Antigravity Sidecar**. Sidecars are long-running background processes that run alongside the agent UI, allowing you to use the exact same programmatic logic without burning prompt tokens or dealing with Keychain constraints.
