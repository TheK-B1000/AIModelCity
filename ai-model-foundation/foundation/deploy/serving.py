"""
Deploy helpers: build serving image, push, update K8s or runtime config.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


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


def deploy_to_target(
    model_name: str,
    version: str,
    artifact_path: str,
    target: str = "staging",
    config: Optional[dict] = None,
) -> None:
    """Placeholder: trigger deploy (e.g. update K8s manifest, apply)."""
    spec = get_serving_spec(model_name, version, artifact_path, target, config)
    # In practice: render k8s template, kubectl apply, or call CD API
    pass
