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
  1. A local `cron` job runs a lightweight shell script every 10-15 minutes.
  2. The script runs `spotticus status`. This CLI command evaluates Spotticus's nuanced heuristics locally (zero token cost)—calculating linear pace, checking absolute floors, and respecting holds, as detailed in [docs/dispatch.md](./dispatch.md).
  3. If capacity exists, it checks the Kanbus backlog for `spot` tasks (zero token cost).
  4. If both exist, it uses the platform's SDK (e.g., the Antigravity Python SDK) to programmatically spawn a sub-agent to do the work.
* **Pros:** Strictly preserves AI tokens for actual coding work.
* **Cons:** Requires a bit more initial setup in the terminal.

---

## Integration: Google Antigravity

To set up the optimal **Pull Model** with Google Antigravity, follow these steps:

### 1. Create the Dispatch Script
Create a bash script (e.g., `~/run_spotticus.sh`) that acts as the bridge between Spotticus and the Antigravity SDK:

```bash
#!/bin/bash
# 1. Check for spare capacity using the Spotticus CLI
cd ~/Projects/Spotticus
SPARE_CAPACITY=$(.venv/bin/spotticus status --threshold=0.10)

if echo "$SPARE_CAPACITY" | grep -q "🟢 ELIGIBLE"; then
    # 2. Check for open 'spot' tasks in your project
    cd ~/Projects/YourProject
    OPEN_TASKS=$(kbs list --status open --label spot --porcelain)
    
    if [ -n "$OPEN_TASKS" ]; then
        # Grab the first task
        FIRST_TASK_ID=$(echo "$OPEN_TASKS" | head -n 1 | awk -F'|' '{print $2}' | xargs)
        
        # Mark it in progress
        kbs update "$FIRST_TASK_ID" --status in_progress
        
        # 3. Invoke the Antigravity Python SDK to spawn a sub-agent
        # Example: python3 spawn_agent.py "$FIRST_TASK_ID"
    fi
fi
```

### 2. Schedule the Script via OS Cron
Make the script executable:
```bash
chmod +x ~/run_spotticus.sh
```

Add it to your user crontab to run every 15 minutes:
```bash
crontab -e
```
Add the following line:
```
*/15 * * * * /bin/bash ~/run_spotticus.sh >> /tmp/spotticus.log 2>&1
```

### 3. Alternative: Antigravity Sidecars
If you prefer to manage the lifecycle of the daemon entirely within Antigravity without touching your OS crontab, you can configure the bash script as an **Antigravity Sidecar**. Sidecars are long-running background processes that run alongside the agent UI, allowing you to use the exact same programmatic logic without burning prompt tokens.
