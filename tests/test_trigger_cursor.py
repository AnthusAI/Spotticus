import json

from tests.trigger_cursor_support import (
    REPO_ROOT,
    SKILL_PATH,
    claimed_target,
    composer_invocation_ok,
    released_target,
    run_trigger_cursor,
)

TARGET = "cursor.cursor-models"


def test_skill_instructs_spot_cursor_workflow():
    text = SKILL_PATH.read_text()
    assert "name: composer-spot-worker" in text
    assert "spot:cursor" in text
    assert "kbs list --status open" in text
    assert "kbs update <id> --status in_progress" in text
    assert "Completed by Composer Spot Worker" in text
    assert "ONE TASK ONLY" in text
    assert "FAIL CLOSED" in text


def test_eligible_pool_claims_invokes_agent_and_releases(tmp_path):
    result = run_trigger_cursor(tmp_path, eligible=True, agent_on_path=True)
    assert result.returncode == 0, result.stderr
    assert claimed_target(result.spotticus_log, TARGET)
    assert "--json" in result.spotticus_log
    argv = json.loads(result.agent_argv)
    composer_invocation_ok(argv, REPO_ROOT)
    assert released_target(result.spotticus_log, TARGET)


def test_missing_agent_fails_closed(tmp_path):
    result = run_trigger_cursor(tmp_path, eligible=True, agent_on_path=False)
    assert result.returncode == 0, result.stderr
    assert "claim " not in result.spotticus_log
    assert result.agent_argv == ""
    assert "Fail closed" in result.stdout or "not on PATH" in result.stdout


def test_ineligible_pool_does_not_dispatch(tmp_path):
    result = run_trigger_cursor(tmp_path, eligible=False, agent_on_path=True)
    assert result.returncode == 0, result.stderr
    assert "claim " not in result.spotticus_log
    assert result.agent_argv == ""
