#!/usr/bin/env python3
"""
Train pipeline: orchestration entrypoint for training a model.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Model name (e.g. fraud_detector)")
    parser.add_argument("--data-path", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    import yaml
    from foundation.core.runner import run_train
    from foundation.core.registry import Registry

    config_path = _REPO_ROOT / "models" / args.model / "model.yaml"
    if not config_path.exists():
        print(f"Missing {config_path}", file=sys.stderr)
        return 1
    config = yaml.safe_load(config_path.read_text()) or {}
    defaults = _REPO_ROOT / "foundation" / "config" / "defaults.yaml"
    if defaults.exists():
        def_cfg = yaml.safe_load(defaults.read_text()) or {}
        for k, v in def_cfg.items():
            if k not in config:
                config[k] = v

    data_path = args.data_path or config.get("data", {}).get("train_path", "data/train.csv")
    artifacts_root = Path(config.get("artifacts", {}).get("root", "./artifacts"))
    import uuid
    run_id = args.run_id or str(uuid.uuid4())[:8]
    output_path = artifacts_root / args.model / run_id
    output_path.mkdir(parents=True, exist_ok=True)

    result = run_train(
        model_name=args.model,
        config=config,
        data_path=str(data_path),
        output_path=str(output_path),
        run_id=run_id,
    )
    run_id = result.get("run_id", run_id)
    reg = Registry(uri=config.get("registry", {}).get("uri", "./registry"))
    reg.log_run(args.model, run_id, metrics=result.get("metrics"), artifact_path=str(output_path))
    print(f"Run ID: {run_id}")
    print("Metrics:", result.get("metrics"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
