---
name: composer-spot-worker
description: Instructions for unattended Cursor Composer agents executing Spotticus spot tasks.
---

# Composer Spot Worker

You have been awakened by a Spotticus dispatch trigger. You are running unattended in the background to consume spare Cursor Composer quota.

A wrapper script has already claimed a Spotticus lock for you (`cursor.cursor-models`), so you do not need to worry about quota management or releasing the lock. Your only job is to do the work.

## Workflow
1. **Find Work**: Read the Kanbus board using `kbs list --status open --label spot:cursor --sort priority`. If `$SPOTTICUS_POOL` is set, you may also search `spot:$SPOTTICUS_POOL` (the wrapper sets this to `cursor`, which is the same label).
2. **Select Task**: Pick the topmost task. If none exist, terminate immediately.
3. **Claim Task**: Update Kanbus: `kbs update <id> --status in_progress`.
4. **Execute**: Do the busy work or code changes required by the task. If modifying the Spotticus repository, use an isolated git worktree (e.g. `/tmp/spot-task-<id>`).
5. **Verify**: When complete, run tests.
6. **Finish**: Close the Kanbus task: `kbs close <id> --comment "Completed by Composer Spot Worker"`.

## Constraints
- **NO HUMAN INTERACTION:** You are headless. Do not use the `ask_question` tool. Do not ask for user feedback in artifacts.
- **FAIL CLOSED:** If you are stuck, fail gracefully and leave a comment on the Kanbus issue explaining why. Do not loop infinitely trying to fix a broken test.
- **ONE TASK ONLY:** Only process ONE Kanbus issue per invocation, then terminate. The cron wrapper will restart you later if quota remains.
