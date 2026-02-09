"""
Tests for fraud_detector features.
"""
import pandas as pd
import pytest
import sys
from pathlib import Path

# Add repo root so we can import the model package
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from models.fraud_detector.features import transform, get_feature_columns


def test_get_feature_columns():
    cols = get_feature_columns()
    assert "amount" in cols
    assert "merchant_id" in cols
    assert "hour" in cols


def test_transform_adds_hour_from_timestamp():
    df = pd.DataFrame({
        "amount": [10.0, 20.0],
        "merchant_id": ["m1", "m2"],
        "timestamp": ["2024-01-01 14:00:00", "2024-01-01 22:30:00"],
    })
    out = transform(df)
    assert "hour" in out.columns
    assert out["hour"].tolist() == [14, 22]


def test_transform_preserves_existing_hour():
    df = pd.DataFrame({
        "amount": [10.0],
        "merchant_id": ["m1"],
        "hour": [12],
    })
    out = transform(df)
    assert out["hour"].tolist() == [12]
