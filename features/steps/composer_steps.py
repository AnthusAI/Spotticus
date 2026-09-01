from behave import given, when, then
from tests.trigger_cursor_support import (
    REPO_ROOT,
    claimed_target,
    composer_invocation_ok,
    released_target,
    run_trigger_cursor,
)


@given(u'the Cursor CLI agent is on PATH')
def step_impl(context):
    context.agent_on_path = True


@given(u'the Cursor CLI agent is not on PATH')
def step_impl(context):
    context.agent_on_path = False


@given(u'the "cursor.cursor-models" pool is eligible')
def step_impl(context):
    context.pool_eligible = True


@given(u'the "cursor.cursor-models" pool is not eligible')
def step_impl(context):
    context.pool_eligible = False


@when(u'the Cursor dispatch wrapper runs')
def step_impl(context):
    import tempfile
    from pathlib import Path

    context.tmp_dir = Path(tempfile.mkdtemp(prefix="trigger-cursor-"))
    context.wrapper = run_trigger_cursor(
        context.tmp_dir,
        eligible=getattr(context, "pool_eligible", False),
        agent_on_path=getattr(context, "agent_on_path", False),
    )


@then(u'a lock is claimed for "cursor.cursor-models"')
def step_impl(context):
    assert context.wrapper.returncode == 0, context.wrapper.stderr
    assert claimed_target(context.wrapper.spotticus_log, "cursor.cursor-models"), (
        context.wrapper.spotticus_log
    )


@then(u'the Cursor CLI is invoked with print mode, model "composer-2.5", and trust')
def step_impl(context):
    import json

    argv = json.loads(context.wrapper.agent_argv)
    composer_invocation_ok(argv, REPO_ROOT)


@then(u'the lock for "cursor.cursor-models" is released')
def step_impl(context):
    assert released_target(context.wrapper.spotticus_log, "cursor.cursor-models"), (
        context.wrapper.spotticus_log
    )


@then(u'no lock is claimed')
def step_impl(context):
    assert context.wrapper.returncode == 0, context.wrapper.stderr
    assert "claim " not in context.wrapper.spotticus_log, context.wrapper.spotticus_log


@then(u'the Cursor CLI is not invoked')
def step_impl(context):
    assert context.wrapper.agent_argv == "", context.wrapper.agent_argv
