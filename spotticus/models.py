from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProbeStatus(Enum):
    OK = "ok"
    FAILED = "failed"


class DataConfidence(Enum):
    EXACT = "exact"
    PERCENT_ONLY = "percentOnly"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class WindowUsage:
    name: str
    is_session: bool
    is_weekly: bool
    used_percent: float
    window_minutes: int
    resets_at: datetime
    reset_description: str

    @property
    def remaining_percent(self) -> float:
        return max(0.0, 100.0 - self.used_percent)


@dataclass(frozen=True)
class ProbeResult:
    provider: str
    status: ProbeStatus
    data_confidence: DataConfidence
    pools: dict[str, list[WindowUsage]] = field(default_factory=dict)
    source: str | None = None
    error: str | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class ProbeReport:
    """Wrapper for a multi-provider probe run."""
    status: ProbeStatus
    results: list[ProbeResult] = field(default_factory=list)
    error: str | None = None


@dataclass(frozen=True)
class SpareScore:
    window_name: str
    elapsed_frac: float
    used_frac: float
    spare: float
    remaining_percent: float
    is_spare: bool


@dataclass(frozen=True)
class PoolScore:
    pool_id: str
    window_scores: list[SpareScore]
    is_eligible: bool
    lock_data: dict | None = None


@dataclass(frozen=True)
class ProviderScore:
    provider: str
    pool_scores: dict[str, PoolScore]
    is_eligible: bool

