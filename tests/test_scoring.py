from datetime import datetime, timedelta, timezone

from spotticus.models import ProbeResult, ProbeStatus, DataConfidence, WindowUsage
from spotticus.scoring import score_window, score_provider


FIXED_NOW = datetime(2026, 9, 1, 12, 0, 0, tzinfo=timezone.utc)

def get_window(used_percent: float, elapsed_minutes: int, window_minutes: int = 10080, name: str = "primary") -> WindowUsage:
    resets_at = FIXED_NOW + timedelta(minutes=(window_minutes - elapsed_minutes))
    return WindowUsage(
        name=name,
        is_session=False,
        is_weekly=True,
        used_percent=used_percent,
        window_minutes=window_minutes,
        resets_at=resets_at,
        reset_description="",
    )



def test_behind_pace_is_spare():
    now = FIXED_NOW
    # 50% elapsed, 20% used. Spare = 0.30
    w = get_window(20.0, 5040)
    score = score_window(w, now, spare_threshold=0.20, remaining_floor=15.0)
    assert score.is_spare
    assert abs(score.spare - 0.30) < 0.001


def test_on_pace_is_not_spare():
    now = FIXED_NOW
    # 50% elapsed, 50% used. Spare = 0.0
    w = get_window(50.0, 5040)
    score = score_window(w, now, spare_threshold=0.20, remaining_floor=15.0)
    assert not score.is_spare
    assert abs(score.spare - 0.0) < 0.001


def test_below_floor_is_not_spare():
    now = FIXED_NOW
    # 90% elapsed, 92% used. remaining = 8%, floor = 15%.
    w = get_window(92.0, 9072)
    score = score_window(w, now, spare_threshold=0.20, remaining_floor=15.0)
    # Even if spare was high (it's not here), remaining < floor makes it false
    assert not score.is_spare


def test_zero_length_window_minutes():
    now = FIXED_NOW
    w = get_window(0.0, 0, window_minutes=0)
    score = score_window(w, now, spare_threshold=0.20, remaining_floor=15.0)
    assert score.elapsed_frac == 1.0


def test_boundary_exact_at_threshold_is_spare():
    now = FIXED_NOW
    # 50% elapsed, 30% used. Spare = 0.20 exactly.
    w = get_window(30.0, 5040)
    score = score_window(w, now, spare_threshold=0.20, remaining_floor=15.0)
    assert score.is_spare


def test_provider_eligible_when_all_windows_spare():
    now = FIXED_NOW
    w1 = get_window(10.0, 5040, name="w1") # spare 0.4
    w2 = get_window(20.0, 5040, name="w2") # spare 0.3
    result = ProbeResult(
        provider="claude",
        status=ProbeStatus.OK,
        data_confidence=DataConfidence.EXACT,
        pools={"default": [w1, w2]},
    )
    score = score_provider(result, now)
    assert score.is_eligible


def test_provider_ineligible_when_one_window_not_spare():
    now = FIXED_NOW
    w1 = get_window(10.0, 5040, name="w1") # spare 0.4 (yes)
    w2 = get_window(50.0, 5040, name="w2") # spare 0.0 (no)
    result = ProbeResult(
        provider="claude",
        status=ProbeStatus.OK,
        data_confidence=DataConfidence.EXACT,
        pools={"default": [w1, w2]},
    )
    score = score_provider(result, now)
    assert not score.is_eligible


def test_provider_ineligible_when_no_windows():
    now = FIXED_NOW
    result = ProbeResult(
        provider="claude",
        status=ProbeStatus.OK,
        data_confidence=DataConfidence.EXACT,
        pools={},
    )
    score = score_provider(result, now)
    assert not score.is_eligible


def test_provider_ineligible_on_probe_failure():
    now = FIXED_NOW
    w1 = get_window(10.0, 5040, name="w1") # spare 0.4
    result = ProbeResult(
        provider="claude",
        status=ProbeStatus.FAILED,
        data_confidence=DataConfidence.UNKNOWN,
        pools={"default": [w1]},
    )
    score = score_provider(result, now)
    assert not score.is_eligible

def test_provider_mixed_pool_eligibility():
    now = FIXED_NOW
    w1 = get_window(10.0, 5040, name="w1") # spare 0.4 (yes)
    w2 = get_window(50.0, 5040, name="w2") # spare 0.0 (no)
    result = ProbeResult(
        provider="antigravity",
        status=ProbeStatus.OK,
        data_confidence=DataConfidence.EXACT,
        pools={"gemini": [w1], "claude": [w2]},
    )
    score = score_provider(result, now)
    assert score.is_eligible is True # Provider is eligible if ANY pool is eligible
    assert score.pool_scores["gemini"].is_eligible is True
    assert score.pool_scores["claude"].is_eligible is False
