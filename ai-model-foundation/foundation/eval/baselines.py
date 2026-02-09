"""
Baseline metrics for eval gates (e.g. heuristic, previous prod model).
Loads from baselines/<model_name>.json when present (Phase 1 regression protection).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional


def _baselines_root() -> Path:
    """Repo root: foundation/eval -> repo root."""
    return Path(__file__).resolve().parent.parent.parent


def get_baseline_metrics(
    model_name: str,
    baseline_name: str,
    config: Optional[dict] = None,
) -> dict[str, float]:
    """
    Return baseline metrics for a model.
    1. Load from baselines/<model_name>.json if it exists (saved when promoted to prod).
    2. Else use config eval.baselines[baseline_name].
    Default: return {} so gate_delta_min 0 allows any metric.
    """
    root = _baselines_root()
    baseline_file = root / "baselines" / f"{model_name}.json"
    if baseline_file.exists():
        try:
            data = json.loads(baseline_file.read_text())
            # File format: {"auc": 0.91, "version": "v3", ...}; drop non-numeric
            return {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}
        except Exception:
            pass
    config = config or {}
    baselines = config.get("eval", {}).get("baselines", {})
    if baseline_name in baselines:
        return dict(baselines[baseline_name])
    return {}
