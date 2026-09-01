import dataclasses
from datetime import datetime, timezone

from spotticus.models import DataConfidence, ProbeStatus, WindowUsage


def test_window_usage_remaining_percent_computed():
    w = WindowUsage(
        name="primary",
        is_session=True,
        is_weekly=False,
        used_percent=25.0,
        window_minutes=300,
        resets_at=datetime.now(timezone.utc),
        reset_description="",
    )
    assert w.remaining_percent == 75.0


def test_window_usage_remaining_percent_clamped_at_zero():
    w = WindowUsage(
        name="primary",
        is_session=True,
        is_weekly=False,
        used_percent=120.0,
        window_minutes=300,
        resets_at=datetime.now(timezone.utc),
        reset_description="",
    )
    assert w.remaining_percent == 0.0


def test_dataclasses_are_frozen():
    w = WindowUsage(
        name="primary",
        is_session=True,
        is_weekly=False,
        used_percent=25.0,
        window_minutes=300,
        resets_at=datetime.now(timezone.utc),
        reset_description="",
    )
    try:
        w.used_percent = 50.0  # type: ignore
        assert False, "Should have raised FrozenInstanceError"
    except dataclasses.FrozenInstanceError:
        pass


def test_enums_match_expected_values():
    assert ProbeStatus.OK.value == "ok"
    assert ProbeStatus.FAILED.value == "failed"
    assert DataConfidence.EXACT.value == "exact"
    assert DataConfidence.PERCENT_ONLY.value == "percentOnly"
    assert DataConfidence.UNKNOWN.value == "unknown"
