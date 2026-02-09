"""
Canary deployment: route a percentage of traffic to new version, compare KPIs.
"""
from __future__ import annotations

from typing import Any, Optional


def canary_spec(
    model_name: str,
    new_version: str,
    current_version: str,
    percent: int = 10,
    config: Optional[dict] = None,
) -> dict[str, Any]:
    """Return canary routing spec (e.g. for service mesh or ingress)."""
    config = config or {}
    percent = config.get("deploy", {}).get("canary_percent", percent)
    return {
        "model_name": model_name,
        "new_version": new_version,
        "current_version": current_version,
        "canary_percent": percent,
    }


def check_canary_kpis(
    canary_metrics: dict[str, float],
    baseline_metrics: dict[str, float],
    kpi_names: Optional[list[str]] = None,
    tolerance_pct: float = 5.0,
) -> tuple[bool, dict]:
    """Compare canary KPIs to baseline. Pass if within tolerance (e.g. no >5% regression)."""
    kpi_names = kpi_names or list(canary_metrics.keys())
    details = {}
    all_ok = True
    for name in kpi_names:
        c = canary_metrics.get(name)
        b = baseline_metrics.get(name)
        if c is None or b is None:
            details[name] = {"passed": True, "reason": "missing"}
            continue
        if b == 0:
            details[name] = {"passed": True, "reason": "no_baseline"}
            continue
        pct_change = (c - b) / b * 100
        passed = pct_change >= -tolerance_pct  # allow up to tolerance_pct regression
        details[name] = {"canary": c, "baseline": b, "pct_change": pct_change, "passed": passed}
        if not passed:
            all_ok = False
    return all_ok, details
