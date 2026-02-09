"""
Observability: drift-lite checks and KPI hooks (errors, latency).
"""
from __future__ import annotations

from collections import deque
from typing import Any, Callable, Optional


class Monitor:
    """Lightweight monitor for drift-lite and KPI hooks."""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.predictions: deque = deque(maxlen=window_size)
        self.latencies: deque = deque(maxlen=window_size)
        self.errors: deque = deque(maxlen=window_size)

    def record_prediction(self, value: float) -> None:
        self.predictions.append(value)

    def record_latency(self, sec: float) -> None:
        self.latencies.append(sec)

    def record_error(self, error: Any) -> None:
        self.errors.append(error)

    def drift_lite(self, reference_mean: Optional[float] = None, reference_std: Optional[float] = None) -> dict:
        """
        Simple drift proxy: mean/std of recent predictions vs reference.
        Returns dict with current_mean, current_std, reference_mean, reference_std, delta_mean.
        """
        if not self.predictions:
            return {}
        import statistics
        current = list(self.predictions)
        mean = statistics.mean(current)
        std = statistics.stdev(current) if len(current) > 1 else 0.0
        out = {"current_mean": mean, "current_std": std}
        if reference_mean is not None:
            out["reference_mean"] = reference_mean
            out["delta_mean"] = mean - reference_mean
        if reference_std is not None:
            out["reference_std"] = reference_std
        return out

    def kpis(self) -> dict[str, Any]:
        """Aggregate KPIs: error_count, latency_p50/p99, prediction_count."""
        out = {"prediction_count": len(self.predictions), "error_count": len(self.errors)}
        if self.latencies:
            sorted_lat = sorted(self.latencies)
            n = len(sorted_lat)
            out["latency_p50"] = sorted_lat[int(0.5 * n)]
            out["latency_p99"] = sorted_lat[int(0.99 * n)] if n >= 100 else sorted_lat[-1]
        return out
