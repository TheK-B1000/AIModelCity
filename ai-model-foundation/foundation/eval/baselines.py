"""
Baseline metrics for eval gates (e.g. heuristic, previous model).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


def get_baseline_metrics(
    model_name: str,
    baseline_name: str,
    config: Optional[dict] = None,
) -> dict[str, float]:
    """
    Return baseline metrics for a model. Can be from config, file, or registry.
    Default: return zeros so any positive metric passes if gate_delta_min is 0.
    """
    config = config or {}
    baselines = config.get("eval", {}).get("baselines", {})
    if baseline_name in baselines:
        return dict(baselines[baseline_name])
    # Optional: load from foundation config or registry
    return {}
