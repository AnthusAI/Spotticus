import abc

from spotticus.models import ProbeReport


class LeftoverProbe(abc.ABC):
    """Abstract base class for leftover probes."""

    @abc.abstractmethod
    def probe(self, targets: list[str] | None = None) -> ProbeReport:
        """Run the probe and return a report."""
        pass
