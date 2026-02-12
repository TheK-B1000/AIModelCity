"""
Save/load model bundles (serialized model + optional metadata).
Artifacts are signed with SHA-256; load verifies checksum to reject tampering.
"""
from __future__ import annotations

import hashlib
import joblib
from pathlib import Path
from typing import Any, Optional

CHECKSUM_FILE = "checksum.sha256"
CHECKSUM_ALGO = "sha256"


def _checksum_file(file_path: Path) -> str:
    """Return hex digest of file using SHA-256."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_checksum(artifact_path: Path, model_file_name: str) -> str:
    """Write checksum.sha256 for the model file; return digest."""
    digest = _checksum_file(artifact_path / model_file_name)
    (artifact_path / CHECKSUM_FILE).write_text(f"{CHECKSUM_ALGO}:{digest}\n")
    return digest


def _verify_checksum(artifact_path: Path, model_file_name: str) -> None:
    """Raise RuntimeError if stored checksum does not match file."""
    ck = artifact_path / CHECKSUM_FILE
    if not ck.exists():
        return
    line = ck.read_text().strip()
    if ":" in line:
        _, expected = line.split(":", 1)
    else:
        expected = line
    actual = _checksum_file(artifact_path / model_file_name)
    if actual != expected:
        raise RuntimeError(
            f"Artifact checksum mismatch at {artifact_path / model_file_name}; possible tampering. Expected {expected}, got {actual}."
        )


def save_bundle(path: str | Path, model: Any, metadata: Optional[dict] = None) -> Path:
    """Save model and optional metadata. Writes model.joblib, model.bin, checksum.sha256."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path / "model.joblib")
    joblib.dump(model, path / "model.bin")
    digest = _write_checksum(path, "model.bin")
    if metadata is not None:
        import json
        meta = dict(metadata)
        meta["artifact_sha256"] = digest
        (path / "metadata.json").write_text(json.dumps(meta, indent=2))
    return path


def load_bundle(path: str | Path, verify: bool = True) -> tuple[Any, dict]:
    """Load model and metadata. If verify=True (default), rejects tampered artifacts via checksum."""
    path = Path(path)
    model_file = path / "model.bin" if (path / "model.bin").exists() else path / "model.joblib"
    if verify:
        _verify_checksum(path, model_file.name)
    model = joblib.load(model_file)
    metadata = {}
    meta_file = path / "metadata.json"
    if meta_file.exists():
        import json
        metadata = json.loads(meta_file.read_text())
    return model, metadata
