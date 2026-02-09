"""
Save/load model bundles (serialized model + optional metadata).
"""
from __future__ import annotations

import joblib
from pathlib import Path
from typing import Any, Optional


def save_bundle(path: str | Path, model: Any, metadata: Optional[dict] = None) -> Path:
    """Save model and optional metadata to a directory. Writes model.joblib and model.bin (same content)."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path / "model.joblib")
    joblib.dump(model, path / "model.bin")  # Phase 1: embedded_models expects model.bin
    if metadata is not None:
        import json
        (path / "metadata.json").write_text(json.dumps(metadata, indent=2))
    return path


def load_bundle(path: str | Path) -> tuple[Any, dict]:
    """Load model and metadata from a bundle directory. Reads model.bin or model.joblib. Returns (model, metadata)."""
    path = Path(path)
    model_file = path / "model.bin" if (path / "model.bin").exists() else path / "model.joblib"
    model = joblib.load(model_file)
    metadata = {}
    meta_file = path / "metadata.json"
    if meta_file.exists():
        import json
        metadata = json.loads(meta_file.read_text())
    return model, metadata
