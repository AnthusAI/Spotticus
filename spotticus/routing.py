from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from spotticus.probes.codexbar import CodexBarProbe
from spotticus.scoring import score_provider


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


def resolve_target(
    class_name: str,
    specific_app: str | None = None,
    config_path: Path | None = None,
    threshold: float = 0.20,
    floor: float = 15.0,
    _mock_is_eligible: Callable[[str], bool] | None = None,
) -> dict[str, str]:
    target_config_path = config_path if config_path is not None else Path.home() / ".spotticus.yml"
    config = load_config(target_config_path)
    classes = config.get("classes", {})
    if class_name not in classes:
        raise ValueError(f"Class '{class_name}' not found in config.")

    targets = classes[class_name]

    if _mock_is_eligible is None:
        probe = CodexBarProbe()
        report = probe.probe()
        if report.status.name == "FAILED":
            raise RuntimeError(f"Probe failed: {report.error}")

        now = datetime.now(timezone.utc)
        provider_scores = {
            res.provider: score_provider(res, now, spare_threshold=threshold, remaining_floor=floor)
            for res in report.results
        }

        def check_eligible(app_name: str) -> bool:
            score = provider_scores.get(app_name)
            return score is not None and score.is_eligible
    else:
        check_eligible = _mock_is_eligible

    for target in targets:
        app = target.get("app")
        if specific_app and app != specific_app:
            continue

        if check_eligible(app):
            return target

    raise RuntimeError("No eligible apps found for the specified class.")
