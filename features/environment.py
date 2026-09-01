import os
import shutil
import subprocess

SPEC_TARGET = "claude.spectest"


def after_scenario(context, scenario):
    # A spec lock left behind would block every later dispatch on this target,
    # so clear it unconditionally (unhold also clears a HELD lock).
    subprocess.run(
        [".venv/bin/spotticus", "unhold", SPEC_TARGET],
        capture_output=True,
        text=True,
    )
    # Spec chores are scaffolding, not backlog; do not leave them on the board.
    task_id = getattr(context, "spec_task_id", "")
    if task_id:
        subprocess.run(
            ["kbs", "delete", task_id, "--yes"],
            capture_output=True,
            text=True,
        )

    spec_dir = getattr(context, "spec_dir", None)
    if spec_dir and os.path.isdir(spec_dir):
        shutil.rmtree(spec_dir, ignore_errors=True)
