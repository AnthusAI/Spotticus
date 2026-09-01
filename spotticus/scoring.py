from datetime import datetime

from spotticus.models import ProbeResult, ProviderScore, SpareScore, WindowUsage


def score_window(
    window: WindowUsage,
    now: datetime,
    spare_threshold: float = 0.20,
    remaining_floor: float = 15.0,
) -> SpareScore:
    """Score a single window to determine if it has spare capacity."""
    if window.window_minutes <= 0:
        elapsed_frac = 1.0
    else:
        seconds_to_reset = (window.resets_at - now).total_seconds()
        elapsed_frac = 1.0 - (seconds_to_reset / (window.window_minutes * 60))

    # Clamp between 0.0 and 1.0
    elapsed_frac = max(0.0, min(1.0, elapsed_frac))

    used_frac = window.used_percent / 100.0
    spare = elapsed_frac - used_frac

    is_spare = (spare >= spare_threshold) and (window.remaining_percent >= remaining_floor)

    return SpareScore(
        window_name=window.name,
        elapsed_frac=elapsed_frac,
        used_frac=used_frac,
        spare=spare,
        remaining_percent=window.remaining_percent,
        is_spare=is_spare,
    )


def score_provider(
    result: ProbeResult,
    now: datetime,
    spare_threshold: float = 0.20,
    remaining_floor: float = 15.0,
) -> ProviderScore:
    """
    Score a provider based on its windows.
    A provider is ONLY eligible if ALL of its windows are spare and it is not locked.
    Failures, missing windows, or active locks result in ineligible.
    """
    from spotticus.models import ProbeStatus
    from spotticus.locks import read_lock

    lock = read_lock(result.provider)
    lock_data = lock.to_dict() if lock else None

    if result.status == ProbeStatus.FAILED or not result.windows:
        return ProviderScore(
            provider=result.provider,
            window_scores=[],
            is_eligible=False,
            lock_data=lock_data
        )

    window_scores = [
        score_window(w, now, spare_threshold, remaining_floor)
        for w in result.windows
    ]

    is_eligible = all(w.is_spare for w in window_scores)
    
    # If locked, it is ineligible
    if lock is not None:
        is_eligible = False

    return ProviderScore(
        provider=result.provider,
        window_scores=window_scores,
        is_eligible=is_eligible,
        lock_data=lock_data
    )
