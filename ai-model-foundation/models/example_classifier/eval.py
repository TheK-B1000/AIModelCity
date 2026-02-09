"""Eval example classifier."""
from __future__ import annotations

from pathlib import Path

from foundation.core.artifacts import load_bundle

from . import features as feat_mod


def run_eval(model_path: str, eval_data_path: str, config: dict, **kwargs) -> dict:
    import pandas as pd
    from sklearn.metrics import accuracy_score, roc_auc_score

    model, metadata = load_bundle(Path(model_path))
    df = pd.read_csv(eval_data_path)
    cols = feat_mod.get_feature_columns()
    target_name = config.get("data_contract", {}).get("target", {}).get("name", "is_fraud")
    X = pd.get_dummies(df[cols], columns=["merchant_id"] if "merchant_id" in cols else [])
    y = df[target_name]
    feature_columns = metadata.get("feature_columns", list(X.columns))
    X = X.reindex(columns=[c for c in feature_columns if c in X.columns], fill_value=0)

    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else pred
    return {
        "metrics": {
            "accuracy": float(accuracy_score(y, pred)),
            "auc": float(roc_auc_score(y, proba)) if len(set(y)) > 1 else 0.0,
        }
    }
