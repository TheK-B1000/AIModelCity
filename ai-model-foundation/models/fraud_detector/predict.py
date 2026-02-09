"""
Prediction entrypoint for fraud_detector. Called by foundation runner / serving.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import pandas as pd

from foundation.core.artifacts import load_bundle

from . import features as feat_mod


def run_predict(
    model_path: str,
    input_data: Union[str, Path, pd.DataFrame, dict],
    **kwargs,
) -> Union[pd.DataFrame, list, dict]:
    """Load model and run inference. input_data can be path to CSV, DataFrame, or dict row."""
    model, metadata = load_bundle(model_path)
    threshold = kwargs.get("threshold") or metadata.get("score_threshold", 0.5)
    feature_columns = metadata.get("feature_columns", feat_mod.get_feature_columns())

    if isinstance(input_data, (str, Path)):
        df = pd.read_csv(input_data)
    elif isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = input_data

    df = feat_mod.transform(df)
    X = pd.get_dummies(df[feat_mod.get_feature_columns()], columns=["merchant_id"] if "merchant_id" in feat_mod.get_feature_columns() else [])
    # Align columns to training (missing -> 0)
    for c in feature_columns:
        if c not in X.columns and c != "merchant_id":
            X[c] = 0
    X = X.reindex(columns=[c for c in feature_columns if c in X.columns], fill_value=0)
    proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)
    score = (proba >= threshold).astype(int).tolist() if hasattr(proba, "__len__") else [1 if proba >= threshold else 0]
    if len(score) == 1 and isinstance(input_data, dict):
        return {"score": score[0], "probability": float(proba[0]) if hasattr(proba, "__len__") else float(proba)}
    return pd.DataFrame({"score": score, "probability": proba if hasattr(proba, "__len__") else [proba]})
