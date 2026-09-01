import os
import shutil
import subprocess

SPEC_TARGET = "claude.spectest"


def _spec_task_ids(context):
    """Every Kanbus id this scenario created, in creation order.

    The dispatch specs track a single chore they also hand to the worker stub
    as SPEC_TASK_ID; the spot queue specs create several per scenario. Collect
    both shapes so neither can outlive the scenario.
    """
    ids = list(getattr(context, "spec_task_ids", []))
    single = getattr(context, "spec_task_id", "")
    if single:
        ids.append(single)
    return list(dict.fromkeys(ids))


def after_scenario(context, scenario):
    # A spec lock left behind would block every later dispatch on this target,
    # so clear it unconditionally (unhold also clears a HELD lock).
    subprocess.run(
        [".venv/bin/spotticus", "unhold", SPEC_TARGET],
        capture_output=True,
        text=True,
    )
    # Spec chores are scaffolding, not backlog; do not leave them on the board.
    # They carry the same spot: labels a worker searches on, so anything left
    # behind gets picked up as real work.
    for task_id in _spec_task_ids(context):
        subprocess.run(
            ["kbs", "delete", task_id, "--yes"],
            capture_output=True,
            text=True,
        )

    spec_dir = getattr(context, "spec_dir", None)
    if spec_dir and os.path.isdir(spec_dir):
        shutil.rmtree(spec_dir, ignore_errors=True)
