"""
Feature transforms for fraud_detector (used by train and predict).
"""
from __future__ import annotations

from typing import Any

import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features from raw input. Idempotent with train and predict."""
    out = df.copy()
    if "hour" not in out.columns and "timestamp" in out.columns:
        out["hour"] = pd.to_datetime(out["timestamp"], errors="coerce").dt.hour.fillna(0).astype(int)
    return out


def get_feature_columns() -> list[str]:
    """Return ordered list of feature names for model input."""
    return ["amount", "merchant_id", "hour"]
