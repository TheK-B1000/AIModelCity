"""
Standardized eval runner: load model, run eval entrypoint, compare to baselines, apply gates.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from ..core.runner import run_eval
from .baselines import get_baseline_metrics
from .metrics import compute_gate_result


def run_harness(
    model_name: str,
    model_path: str,
    eval_data_path: str,
    config: dict,
    baseline_name: Optional[str] = None,
    gate_metrics: Optional[list[str]] = None,
    **kwargs: Any,
) -> dict:
    """
    Run model eval, optionally compare to baseline, and compute gate pass/fail.
    Returns dict with metrics, baseline_metrics, gate_passed, gate_details.
    """
    result = run_eval(
        model_name=model_name,
        model_path=model_path,
        eval_data_path=eval_data_path,
        config=config,
        **kwargs,
    )
    metrics = result.get("metrics", result)
    baseline_metrics = get_baseline_metrics(model_name, baseline_name or "heuristic", config)
    gate_metrics = gate_metrics or list(metrics.keys())
    gate_passed, gate_details = compute_gate_result(metrics, baseline_metrics, gate_metrics, config)
    return {
        "metrics": metrics,
        "baseline_metrics": baseline_metrics,
        "gate_passed": gate_passed,
        "gate_details": gate_details,
    }
