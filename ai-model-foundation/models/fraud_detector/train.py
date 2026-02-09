"""
Training entrypoint for fraud_detector. Called by foundation runner.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from foundation.core.artifacts import save_bundle

# Import from same package
from . import features as feat_mod


def run_train(
    config: dict,
    data_path: str,
    output_path: str,
    **kwargs,
) -> dict:
    """Train model and save bundle. Returns run_id and metrics."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, roc_auc_score

    df = pd.read_csv(data_path)
    df = feat_mod.transform(df)
    cols = feat_mod.get_feature_columns()
    X = pd.get_dummies(df[cols], columns=["merchant_id"] if "merchant_id" in cols else [])
    y = df[config.get("data_contract", {}).get("target", {}).get("name", "is_fraud")]

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else pred

    metrics = {
        "accuracy": float(accuracy_score(y, pred)),
        "auc": float(roc_auc_score(y, proba)) if len(set(y)) > 1 else 0.0,
    }
    run_id = kwargs.get("run_id") or str(uuid.uuid4())[:8]
    save_bundle(
        output_path,
        model,
        metadata={"run_id": run_id, "metrics": metrics, "feature_columns": list(X.columns)},
    )
    return {"run_id": run_id, "metrics": metrics}
