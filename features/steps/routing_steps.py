import tempfile
from pathlib import Path

from behave import given, then, when
import yaml

from spotticus.routing import resolve_target

@given('a local configuration file with a "{class_name}" class:')
def step_impl(context, class_name):
    # Parse the table into a list of dicts
    targets = []
    for row in context.table:
        targets.append(dict(row.as_dict()))
        
    config = {
        "classes": {
            class_name: targets
        }
    }
    
    # Write to a temporary file
    fd, path = tempfile.mkstemp(suffix=".yml")
    with open(path, "w") as f:
        import yaml
        yaml.dump(config, f)
        
    context.config_path = Path(path)
    context.mock_eligibility = {}
    
@given('the "{pool_id}" routing pool is eligible')
def step_impl(context, pool_id):
    context.mock_eligibility[pool_id] = True
    
@given('the "{pool_id}" routing pool is NOT eligible')
def step_impl(context, pool_id):
    context.mock_eligibility[pool_id] = False
    
@when('Spotticus resolves the "{class_name}" class')
def step_impl(context, class_name):
    _resolve(context, class_name)

@when('Spotticus resolves the "{class_name}" class explicitly for the "{app_name}" app')
def step_impl(context, class_name, app_name):
    _resolve(context, class_name, app_name)

def _resolve(context, class_name, specific_app=None):
    try:
        # We need to mock the probe or score_provider inside resolve_target
        # Since we just want to test routing logic, we can pass a mock checker
        def mock_is_eligible(app_name):
            # In our tests, we use "app.pool" in the Given step (e.g. antigravity.gemini).
            # If the app name is passed, we check if any pool for this app is eligible.
            for key, val in context.mock_eligibility.items():
                if key.startswith(app_name + ".") and val:
                    return True
            return False

        context.resolve_result = resolve_target(
            class_name=class_name,
            specific_app=specific_app,
            config_path=context.config_path,
            _mock_is_eligible=mock_is_eligible
        )
        context.resolve_error = None
    except Exception as e:
        context.resolve_result = None
        context.resolve_error = str(e)
        
@then('it returns the "{expected}" app')
def step_impl(context, expected):
    assert context.resolve_result is not None, f"Expected success but got error: {context.resolve_error}"
    assert context.resolve_result["app"] == expected, f"Expected {expected}, got {context.resolve_result['app']}"
    
@then('it returns the "{expected}" model')
def step_impl(context, expected):
    assert context.resolve_result is not None
    assert context.resolve_result["model"] == expected, f"Expected {expected}, got {context.resolve_result['model']}"
    
@then('it returns an error indicating no eligible apps')
def step_impl(context):
    assert context.resolve_result is None, f"Expected error but got {context.resolve_result}"
    assert "No eligible apps" in context.resolve_error
