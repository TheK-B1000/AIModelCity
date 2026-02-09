"""Train example classifier (sklearn)."""
from __future__ import annotations

from pathlib import Path

from foundation.core.artifacts import save_bundle

from . import features as feat_mod


def run_train(config: dict, data_path: str, output_path: str, **kwargs) -> dict:
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, roc_auc_score

    run_id = kwargs.get("run_id", "unknown")
    df = pd.read_csv(data_path)
    cols = feat_mod.get_feature_columns()
    X = pd.get_dummies(df[cols], columns=["merchant_id"] if "merchant_id" in cols else [])
    target_name = config.get("data_contract", {}).get("target", {}).get("name", "is_fraud")
    y = df[target_name]

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else pred

    metrics = {
        "accuracy": float(accuracy_score(y, pred)),
        "auc": float(roc_auc_score(y, proba)) if len(set(y)) > 1 else 0.0,
    }
    save_bundle(
        Path(output_path),
        model,
        metadata={"run_id": run_id, "metrics": metrics, "feature_columns": list(X.columns)},
    )
    return {"run_id": run_id, "metrics": metrics}
