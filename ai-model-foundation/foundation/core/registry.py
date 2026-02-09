"""
Registry: MLflow (Registry Hall) or local file index for model runs and versions.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

# Optional MLflow
try:
    import mlflow
    _MLFLOW_AVAILABLE = True
except ImportError:
    _MLFLOW_AVAILABLE = False
    mlflow = None


class Registry:
    """MLflow backend (Registry Hall) or local file index."""

    def __init__(self, backend: str = "local", uri: str = "./registry"):
        self.backend = backend
        self.uri = uri.rstrip("/") if backend == "mlflow" else uri
        # Local index: when mlflow, use ./registry for run_id -> mlflow_run_id and artifact_path
        self._local_uri = Path("./registry") if backend == "mlflow" else Path(uri)
        if backend == "local":
            self._local_uri.mkdir(parents=True, exist_ok=True)
        else:
            self._local_uri.mkdir(parents=True, exist_ok=True)
        if backend == "mlflow" and _MLFLOW_AVAILABLE:
            mlflow.set_tracking_uri(self.uri)

    def log_run(
        self,
        model_name: str,
        run_id: str,
        metrics: Optional[dict[str, float]] = None,
        params: Optional[dict[str, Any]] = None,
        artifact_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Record a run. Returns MLflow run_id (UUID) when backend is mlflow, else None.
        Local backend: writes to registry dir. MLflow: creates a run and logs params/metrics/artifacts.
        """
        if self.backend == "local":
            run_dir = self._local_uri / model_name / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            if metrics is not None:
                (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
            if params is not None:
                (run_dir / "params.json").write_text(json.dumps(params, indent=2))
            if artifact_path is not None:
                (run_dir / "artifact_path.txt").write_text(artifact_path)
            return None
        if self.backend == "mlflow" and _MLFLOW_AVAILABLE:
            with mlflow.start_run(run_name=run_id) as run:
                if params:
                    mlflow.log_params({k: str(v) for k, v in params.items()})
                if metrics:
                    mlflow.log_metrics(metrics)
                if artifact_path and Path(artifact_path).exists():
                    mlflow.log_artifacts(artifact_path, artifact_path="artifact")
                mlflow_run_id = run.info.run_id
            # Store MLflow run_id and copy metadata locally so get_run works
            local_dir = Path(self._local_uri) / model_name / run_id
            local_dir.mkdir(parents=True, exist_ok=True)
            (local_dir / "mlflow_run_id.txt").write_text(mlflow_run_id)
            if artifact_path is not None:
                (local_dir / "artifact_path.txt").write_text(artifact_path)
            if metrics is not None:
                (local_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
            if params is not None:
                (local_dir / "params.json").write_text(json.dumps(params, indent=2))
            return mlflow_run_id
        return None

    def get_run(self, model_name: str, run_id: str) -> dict[str, Any]:
        """Load run metadata and artifact path. Resolves from local index (and MLflow run_id if needed)."""
        run_dir = self._local_uri / model_name / run_id
        out = {"run_id": run_id, "model_name": model_name}
        if (run_dir / "metrics.json").exists():
            out["metrics"] = json.loads((run_dir / "metrics.json").read_text())
        if (run_dir / "params.json").exists():
            out["params"] = json.loads((run_dir / "params.json").read_text())
        if (run_dir / "artifact_path.txt").exists():
            out["artifact_path"] = (run_dir / "artifact_path.txt").read_text().strip()
        if (run_dir / "mlflow_run_id.txt").exists():
            out["mlflow_run_id"] = (run_dir / "mlflow_run_id.txt").read_text().strip()
        return out

    def list_runs(self, model_name: str, limit: int = 100) -> list[str]:
        """List run IDs for a model (from local index)."""
        if self.backend != "local":
            model_dir = self._local_uri / model_name
        else:
            model_dir = self._local_uri / model_name
        if not model_dir.exists():
            return []
        return sorted(os.listdir(model_dir), reverse=True)[:limit]

    def register_run(
        self,
        model_name: str,
        run_id: str,
        stage: str = "dev",
    ) -> Optional[str]:
        """
        Register the run as a model version in MLflow and set stage.
        Requires backend=mlflow and run to have been logged (so mlflow_run_id exists).
        Returns version string (e.g. "1") or None.
        """
        if not _MLFLOW_AVAILABLE or self.backend != "mlflow":
            return None
        run_dir = self._local_uri / model_name / run_id
        mlflow_run_id_file = run_dir / "mlflow_run_id.txt"
        if not mlflow_run_id_file.exists():
            return None
        mlflow_run_id = mlflow_run_id_file.read_text().strip()
        mlflow.set_tracking_uri(self.uri)
        try:
            result = mlflow.register_model(f"runs:/{mlflow_run_id}/artifact", model_name)
            version = result.version
            client = mlflow.tracking.MlflowClient()
            # MLflow stages: Staging, Production
            stage_map = {"staging": "Staging", "prod": "Production"}
            mlflow_stage = stage_map.get(stage)
            if mlflow_stage:
                client.transition_model_version_stage(model_name, version, mlflow_stage)
            return version
        except Exception:
            return None