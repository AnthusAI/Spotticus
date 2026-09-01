import subprocess
import time
import sys
import os

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def main():
    print("🤖 Agent awake. Checking Spotticus oracle for spare capacity...")
    # Lowering the threshold to 0.10 to ensure Cursor is eligible for this test
    status = run_cmd(".venv/bin/spotticus status --threshold=0.10")
    
    # Simple check if Cursor is eligible
    if "CURSOR" not in status.stdout or "🟢 ELIGIBLE" not in status.stdout.split("CURSOR")[1].split("\n")[0]:
        print("💤 No capacity available above thresholds. Going back to sleep.")
        return

    print("🟢 Capacity found on CURSOR! Attempting claim...")
    pid = os.getpid()
    
    # 1. Claim the lock
    claim = run_cmd(f".venv/bin/spotticus claim cursor --pid {pid} --product Antigravity --model '3.1 Pro' --name 'SpotTester'")
    if claim.returncode != 0:
        print(f"❌ Claim failed. Another agent might be running: {claim.stderr}")
        return

    try:
        print("✅ Claim successful. Fetching Kanbus tasks...")
        
        # 2. Check Kanbus for open spot tasks
        kbs_out = run_cmd("kbs list --status open --label spot --porcelain")
        tasks = [line for line in kbs_out.stdout.strip().split('\n') if line]
        if not tasks:
            print("📭 No open spot tasks in Kanbus. Exiting.")
            return
        
        # 3. Parse and claim the first Kanbus task
        first_task = tasks[0]
        # Format: Type | ID | Parent | Status | Priority | Title
        parts = [p.strip() for p in first_task.split('|')]
        task_id = parts[1]
        task_title = parts[5]
        
        print(f"📋 Found Kanbus task {task_id}: {task_title}")
        print("⏳ Marking in_progress...")
        run_cmd(f"kbs update {task_id} --status in_progress")
        
        # 4. Do the busy work
        print(f"⚙️  Executing busy work for '{task_title}'...")
        time.sleep(3)
        print("✨ Work complete.")
        
        # 5. Close the task
        run_cmd(f"kbs close {task_id}")
        run_cmd(f"kbs comment {task_id} 'Completed by SpotTester'")
        print(f"🔒 Closed Kanbus task {task_id}.")
        
    finally:
        # 6. Release the lock so others can use the pool
        print("🔓 Releasing Spotticus lock...")
        run_cmd(f".venv/bin/spotticus release cursor --pid {pid}")

if __name__ == "__main__":
    main()
