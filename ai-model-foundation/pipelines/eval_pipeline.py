#!/usr/bin/env python3
"""
Eval pipeline: run evaluation and gates for a trained model.
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
    parser.add_argument("--model", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--eval-data", default=None)
    args = parser.parse_args()

    import yaml
    from foundation.core.registry import Registry
    from foundation.eval.harness import run_harness

    config_path = _REPO_ROOT / "models" / args.model / "model.yaml"
    config = yaml.safe_load(config_path.read_text()) or {} if config_path.exists() else {}
    defaults = _REPO_ROOT / "foundation" / "config" / "defaults.yaml"
    if defaults.exists():
        def_cfg = yaml.safe_load(defaults.read_text()) or {}
        for k, v in def_cfg.items():
            if k not in config:
                config[k] = v

    runs_root = Path(config.get("runs", {}).get("root") or config.get("artifacts", {}).get("root", "./runs"))
    reg = Registry(uri=config.get("registry", {}).get("uri", "./registry"))
    run = reg.get_run(args.model, args.run_id)
    model_path = run.get("artifact_path") or str(runs_root / args.run_id / "artifact")
    eval_data = args.eval_data or config.get("data", {}).get("eval_path", "data/eval.csv")

    result = run_harness(
        model_name=args.model,
        model_path=model_path,
        eval_data_path=eval_data,
        config=config,
    )
    print("gate_passed:", result["gate_passed"])
    print("metrics:", result["metrics"])
    print("gate_details:", result["gate_details"])
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
