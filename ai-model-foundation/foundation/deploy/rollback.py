"""
Rollback: switch serving to a previous model version.
"""
from __future__ import annotations

from typing import Optional

from ..core.registry import Registry
from .serving import deploy_to_target


def rollback_to_version(
    model_name: str,
    to_version: str,
    registry: Optional[Registry] = None,
    config: Optional[dict] = None,
) -> None:
    """
    Deploy the specified version to prod (rollback). Optionally resolve
    artifact_path from registry.
    """
    registry = registry or Registry()
    run = registry.get_run(model_name, to_version)
    artifact_path = run.get("artifact_path") or f"./artifacts/{model_name}/{to_version}"
    deploy_to_target(
        model_name=model_name,
        version=to_version,
        artifact_path=artifact_path,
        target="prod",
        config=config,
    )


def get_previous_versions(model_name: str, current_version: str, limit: int = 10) -> list[str]:
    """List previous run/version IDs for a model (for choosing rollback target)."""
    reg = Registry()
    runs = reg.list_runs(model_name, limit=limit)
    return [r for r in runs if r != current_version][:limit]
