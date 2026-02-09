#!/usr/bin/env python3
"""
Foundation CLI: train, eval, validate, deploy (and rollback).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add repo root so foundation and models are importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _load_config(model_name: str | None) -> dict:
    import yaml
    defaults = _REPO_ROOT / "foundation" / "config" / "defaults.yaml"
    config = {}
    if defaults.exists():
        config = yaml.safe_load(defaults.read_text()) or {}
    if model_name:
        model_yaml = _REPO_ROOT / "models" / model_name / "model.yaml"
        if model_yaml.exists():
            model_cfg = yaml.safe_load(model_yaml.read_text()) or {}
            for k, v in model_cfg.items():
                if isinstance(v, dict) and k in config and isinstance(config[k], dict):
                    config[k] = {**config[k], **v}
                else:
                    config[k] = v
    return config


def cmd_validate(args: argparse.Namespace) -> int:
    from foundation.data.contracts import load_contract_from_dict
    from foundation.data.validate import validate_dataframe
    import pandas as pd
    config = _load_config(args.model)
    contract_dict = config.get("data_contract", {})
    if not contract_dict:
        print("No data_contract in model config", file=sys.stderr)
        return 1
    contract = load_contract_from_dict(contract_dict)
    df = pd.read_csv(args.data)
    errors = validate_dataframe(df, contract)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print("Validation passed.")
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    from foundation.core.runner import run_train
    from foundation.core.registry import Registry
    from foundation.core.artifacts import save_bundle
    import uuid
    config = _load_config(args.model)
    data_path = getattr(args, "data_path", None) or config.get("data", {}).get("train_path", "data/train.csv")
    artifacts_root = Path(config.get("artifacts", {}).get("root", "./artifacts"))
    output_path = artifacts_root / args.model / (args.run_id or str(uuid.uuid4())[:8])
    output_path.mkdir(parents=True, exist_ok=True)
    result = run_train(
        model_name=args.model,
        config=config,
        data_path=str(data_path),
        output_path=str(output_path),
    )
    reg = Registry(uri=config.get("registry", {}).get("uri", "./registry"))
    run_id = result.get("run_id", output_path.name)
    reg.log_run(args.model, run_id, metrics=result.get("metrics"), artifact_path=str(output_path))
    print(f"Run ID: {run_id}, artifact: {output_path}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    from foundation.core.registry import Registry
    from foundation.eval.harness import run_harness
    config = _load_config(args.model)
    reg = Registry(uri=config.get("registry", {}).get("uri", "./registry"))
    run = reg.get_run(args.model, args.run_id)
    model_path = run.get("artifact_path") or str(Path(config.get("artifacts", {}).get("root", "./artifacts")) / args.model / args.run_id)
    eval_data = getattr(args, "eval_data", None) or config.get("data", {}).get("eval_path", "data/eval.csv")
    result = run_harness(
        model_name=args.model,
        model_path=model_path,
        eval_data_path=eval_data,
        config=config,
    )
    print("gate_passed:", result["gate_passed"])
    print("metrics:", result["metrics"])
    return 0 if result["gate_passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="foundation")
    sub = parser.add_subparsers(dest="command", required=True)
    # validate
    p_val = sub.add_parser("validate")
    p_val.add_argument("--model", required=True)
    p_val.add_argument("--data", required=True)
    p_val.set_defaults(func=cmd_validate)
    # train
    p_train = sub.add_parser("train")
    p_train.add_argument("--model", required=True)
    p_train.add_argument("--run-id", default=None)
    p_train.add_argument("--data-path", default=None)
    p_train.set_defaults(func=cmd_train)
    # eval
    p_eval = sub.add_parser("eval")
    p_eval.add_argument("--model", required=True)
    p_eval.add_argument("--run-id", required=True)
    p_eval.add_argument("--eval-data", default=None)
    p_eval.set_defaults(func=cmd_eval)
    # deploy / rollback can be added similarly
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
