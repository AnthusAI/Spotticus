from datetime import datetime

from spotticus.models import ProbeResult, ProviderScore, PoolScore, SpareScore, WindowUsage


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
    Score a provider based on its windows and pools.
    """
    from spotticus.models import ProbeStatus
    from spotticus.locks import read_lock

    if result.status == ProbeStatus.FAILED or not result.pools:
        return ProviderScore(
            provider=result.provider,
            pool_scores={},
            is_eligible=False
        )

    pool_scores = {}
    provider_eligible = False

    for pool_id, windows in result.pools.items():
        lock = read_lock(f"{result.provider}.{pool_id}")
        lock_data = lock.to_dict() if lock else None

        window_scores = [
            score_window(w, now, spare_threshold, remaining_floor)
            for w in windows
        ]

        is_eligible = bool(window_scores) and all(w.is_spare for w in window_scores)
        
        # If locked, it is ineligible
        if lock is not None:
            is_eligible = False

        if is_eligible:
            provider_eligible = True

        pool_scores[pool_id] = PoolScore(
            pool_id=pool_id,
            window_scores=window_scores,
            is_eligible=is_eligible,
            lock_data=lock_data
        )

    return ProviderScore(
        provider=result.provider,
        pool_scores=pool_scores,
        is_eligible=provider_eligible
    )
