"""
Eval metrics and gate logic (compare to baselines).
"""
from __future__ import annotations

from typing import Any, Optional


def compute_gate_result(
    metrics: dict[str, float],
    baseline_metrics: dict[str, float],
    gate_metric_names: list[str],
    config: Optional[dict] = None,
) -> tuple[bool, dict[str, Any]]:
    """
    Determine if gates pass: for each gate metric, model should be >= baseline (or meet min delta).
    Returns (all_passed, details).
    """
    config = config or {}
    gate_delta_min = config.get("eval", {}).get("gate_delta_min", 0.0)
    details = {}
    all_passed = True
    for name in gate_metric_names:
        val = metrics.get(name)
        base = baseline_metrics.get(name)
        if val is None:
            details[name] = {"passed": False, "reason": "missing_metric"}
            all_passed = False
            continue
        if base is None:
            details[name] = {"passed": True, "reason": "no_baseline"}
            continue
        delta = val - base
        passed = delta >= gate_delta_min
        details[name] = {"value": val, "baseline": base, "delta": delta, "passed": passed}
        if not passed:
            all_passed = False
    return all_passed, details
