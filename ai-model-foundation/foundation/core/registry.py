"""
Registry wrapper: MLflow or simple DB for model runs and metadata.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional


class Registry:
    """Wrapper around MLflow or a simple file-based registry."""

    def __init__(self, backend: str = "local", uri: str = "./registry"):
        self.backend = backend
        self.uri = Path(uri)
        if backend == "local":
            self.uri.mkdir(parents=True, exist_ok=True)

    def log_run(
        self,
        model_name: str,
        run_id: str,
        metrics: Optional[dict[str, float]] = None,
        params: Optional[dict[str, Any]] = None,
        artifact_path: Optional[str] = None,
    ) -> None:
        """Record a run (train or eval) with optional artifact path."""
        if self.backend == "local":
            run_dir = self.uri / model_name / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            if metrics is not None:
                (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
            if params is not None:
                (run_dir / "params.json").write_text(json.dumps(params, indent=2))
            if artifact_path is not None:
                (run_dir / "artifact_path.txt").write_text(artifact_path)
        # else: MLflow client.log_artifact, log_metric, etc.

    def get_run(self, model_name: str, run_id: str) -> dict[str, Any]:
        """Load run metadata (and optionally artifact path)."""
        if self.backend == "local":
            run_dir = self.uri / model_name / run_id
            out = {"run_id": run_id, "model_name": model_name}
            if (run_dir / "metrics.json").exists():
                out["metrics"] = json.loads((run_dir / "metrics.json").read_text())
            if (run_dir / "params.json").exists():
                out["params"] = json.loads((run_dir / "params.json").read_text())
            if (run_dir / "artifact_path.txt").exists():
                out["artifact_path"] = (run_dir / "artifact_path.txt").read_text().strip()
            return out
        return {}

    def list_runs(self, model_name: str, limit: int = 100) -> list[str]:
        """List run IDs for a model (e.g. for eval or rollback)."""
        if self.backend == "local":
            model_dir = self.uri / model_name
            if not model_dir.exists():
                return []
            return sorted(os.listdir(model_dir), reverse=True)[:limit]
        return []
