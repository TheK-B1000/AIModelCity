"""
Deploy helpers: copy artifact to deployments/embedded/ (Phase 1), and optional K8s/serving.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Optional


def _deployments_root() -> Path:
    """Repo root for deployments/ (embedded, future channels, etc.)."""
    return Path(__file__).resolve().parent.parent.parent


def _baselines_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def get_serving_spec(
    model_name: str,
    version: str,
    artifact_path: str,
    target: str = "staging",
    config: Optional[dict] = None,
) -> dict[str, Any]:
    """Return a spec dict for serving (image, env, replicas, resource limits)."""
    config = config or {}
    deploy_cfg = config.get("deploy", {})
    replicas = deploy_cfg.get("staging_replicas", 1) if target == "staging" else deploy_cfg.get("prod_replicas", 2)
    return {
        "model_name": model_name,
        "version": version,
        "artifact_path": artifact_path,
        "target": target,
        "replicas": replicas,
        "env": {
            "MODEL_NAME": model_name,
            "MODEL_VERSION": version,
            "ARTIFACT_PATH": artifact_path,
        },
    }


def deploy_to_embedded(
    model_name: str,
    run_id: str,
    artifact_path: str,
    stage: str = "staging",
    metrics: Optional[dict] = None,
    config: Optional[dict] = None,
) -> Path:
    """
    Copy artifact from runs/<run_id>/artifact/ to deployments/embedded/<model_name>/model.bin.
    If stage is prod, save baseline to baselines/<model_name>.json.
    Returns path to deployments/embedded/<model_name>/model.bin.
    """
    root = _deployments_root()
    embedded_dir = root / "deployments" / "embedded" / model_name
    embedded_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = Path(artifact_path)
    # Copy model, metadata, and checksum so embedded app can load_bundle() with verification
    src_bin = artifact_dir / "model.bin" if (artifact_dir / "model.bin").exists() else artifact_dir / "model.joblib"
    if src_bin.exists():
        shutil.copy2(src_bin, embedded_dir / "model.bin")
    if (artifact_dir / "metadata.json").exists():
        shutil.copy2(artifact_dir / "metadata.json", embedded_dir / "metadata.json")
    if (artifact_dir / "checksum.sha256").exists():
        shutil.copy2(artifact_dir / "checksum.sha256", embedded_dir / "checksum.sha256")
    # Record what is deployed (for "what model is in staging?")
    deploy_meta = {"model_name": model_name, "version": run_id, "stage": stage, "artifact_path": str(artifact_path)}
    (embedded_dir / "deploy_meta.json").write_text(json.dumps(deploy_meta, indent=2))
    if stage == "prod" and metrics:
        baselines_dir = _baselines_root() / "baselines"
        baselines_dir.mkdir(parents=True, exist_ok=True)
        baseline_file = baselines_dir / f"{model_name}.json"
        baseline_file.write_text(json.dumps({"version": run_id, **metrics}, indent=2))
    return embedded_dir / "model.bin"


def deploy_to_target(
    model_name: str,
    version: str,
    artifact_path: str,
    target: str = "staging",
    metrics: Optional[dict] = None,
    config: Optional[dict] = None,
) -> None:
    """Copy to deployments/embedded (and save baseline if target=prod). Optionally trigger K8s."""
    deploy_to_embedded(model_name, version, artifact_path, stage=target, metrics=metrics, config=config)
