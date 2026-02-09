"""Predict with example classifier."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import pandas as pd

from foundation.core.artifacts import load_bundle

from . import features as feat_mod


def run_predict(model_path: str, input_data: Union[str, Path, pd.DataFrame, dict], **kwargs) -> Any:
    model, metadata = load_bundle(Path(model_path))
    if isinstance(input_data, (str, Path)):
        df = pd.read_csv(input_data)
    elif isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = input_data
    cols = feat_mod.get_feature_columns()
    X = pd.get_dummies(df[cols], columns=["merchant_id"] if "merchant_id" in cols else [])
    feature_columns = metadata.get("feature_columns", list(X.columns))
    X = X.reindex(columns=[c for c in feature_columns if c in X.columns], fill_value=0)
    proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)
    if isinstance(input_data, dict) and len(proba) == 1:
        return {"score": int(proba[0] >= 0.5), "probability": float(proba[0])}
    return pd.DataFrame({"score": (proba >= 0.5).astype(int), "probability": proba})
