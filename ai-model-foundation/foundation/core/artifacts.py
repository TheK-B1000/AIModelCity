"""
Save/load model bundles (serialized model + optional metadata).
"""
from __future__ import annotations

import joblib
from pathlib import Path
from typing import Any, Optional


def save_bundle(path: str | Path, model: Any, metadata: Optional[dict] = None) -> Path:
    """Save model and optional metadata to a directory."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path / "model.joblib")
    if metadata is not None:
        import json
        (path / "metadata.json").write_text(json.dumps(metadata, indent=2))
    return path


def load_bundle(path: str | Path) -> tuple[Any, dict]:
    """Load model and metadata from a bundle directory. Returns (model, metadata)."""
    path = Path(path)
    model = joblib.load(path / "model.joblib")
    metadata = {}
    meta_file = path / "metadata.json"
    if meta_file.exists():
        import json
        metadata = json.loads(meta_file.read_text())
    return model, metadata
