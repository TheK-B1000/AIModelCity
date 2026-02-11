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
    from foundation.data.validate import validate_dataframe, load_contract_from_dict
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


def _run_dir(config: dict, run_id: str) -> Path:
    """Canonical run directory: runs/<run_id>/ (with artifact/ inside)."""
    runs_root = Path(config.get("runs", {}).get("root") or config.get("artifacts", {}).get("root", "./runs"))
    return runs_root / run_id


def cmd_train(args: argparse.Namespace) -> int:
    from foundation.core.runner import run_train
    from foundation.core.registry import Registry
    from datetime import datetime
    import json
    config = _load_config(args.model)
    dataset = getattr(args, "dataset", None) or "default"
    data_path = getattr(args, "data_path", None) or config.get("data", {}).get("train_path", "data/train.csv")
    # Phase 1: reproducible run_id = model_YYYYMMDD_HHMMSS
    run_id = args.run_id or f"{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = _run_dir(config, run_id)
    output_path = run_dir / "artifact"
    output_path.mkdir(parents=True, exist_ok=True)
    result = run_train(
        model_name=args.model,
        config=config,
        data_path=str(data_path),
        output_path=str(output_path),
        run_id=run_id,
        dataset=dataset,
    )
    run_id = result.get("run_id", run_id)
    metrics = result.get("metrics") or {}
    params = {"model": args.model, "dataset": dataset, "data_path": data_path, "run_id": run_id}
    meta = {"run_id": run_id, "model_name": args.model, "dataset": dataset, "artifact_path": str(output_path)}
    meta["timestamp"] = datetime.now().isoformat()
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (run_dir / "params.json").write_text(json.dumps(params, indent=2))
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    reg = Registry(backend=config.get("registry", {}).get("backend", "local"), uri=config.get("registry", {}).get("uri", "./registry"))
    reg.log_run(args.model, run_id, metrics=metrics, params=params, artifact_path=str(output_path))
    print(f"Run ID: {run_id}, run_dir: {run_dir}")
    return 0


# Exit code for eval gate failure (CI depends on it)
EVAL_GATE_FAIL_EXIT_CODE = 12


def cmd_eval(args: argparse.Namespace) -> int:
    from foundation.core.registry import Registry
    from foundation.eval.harness import run_harness
    config = _load_config(args.model)
    reg = Registry(backend=config.get("registry", {}).get("backend", "local"), uri=config.get("registry", {}).get("uri", "./registry"))
    run = reg.get_run(args.model, args.run_id)
    run_dir = _run_dir(config, args.run_id)
    default_artifact = run_dir / "artifact"
    model_path = run.get("artifact_path") or str(default_artifact)
    eval_data = getattr(args, "eval_data", None) or config.get("data", {}).get("eval_path", "data/eval.csv")
    result = run_harness(
        model_name=args.model,
        model_path=model_path,
        eval_data_path=eval_data,
        config=config,
    )
    print("gate_passed:", result["gate_passed"])
    print("metrics:", result["metrics"])
    if not result["gate_passed"]:
        print("Eval gates failed; CI would block promotion.", file=sys.stderr)
    return 0 if result["gate_passed"] else EVAL_GATE_FAIL_EXIT_CODE


def cmd_register(args: argparse.Namespace) -> int:
    """Register a run in MLflow and set stage (dev/staging/prod)."""
    import json
    from foundation.core.registry import Registry
    config = _load_config(args.model)
    reg = Registry(backend="mlflow", uri=config.get("registry", {}).get("uri", "http://127.0.0.1:5000"))
    run_id = args.run_id
    run_dir = _run_dir(config, run_id)
    run_info = reg.get_run(args.model, run_id)
    if not run_info.get("mlflow_run_id") and run_dir.exists():
        metrics = json.loads((run_dir / "metrics.json").read_text()) if (run_dir / "metrics.json").exists() else {}
        params = json.loads((run_dir / "params.json").read_text()) if (run_dir / "params.json").exists() else {}
        artifact_path = run_dir / "artifact"
        reg.log_run(args.model, run_id, metrics=metrics, params=params, artifact_path=str(artifact_path))
    version = reg.register_run(args.model, run_id, stage=args.stage)
    if version:
        print(f"Registered {args.model} version {version} in stage '{args.stage}'. See MLflow UI.")
        return 0
    print("Registration failed. Is MLflow running (mlflow ui) and backend=mlflow?", file=sys.stderr)
    return 1


def cmd_deploy(args: argparse.Namespace) -> int:
    """Copy artifact to deployments/embedded/<model>/model.bin and optionally save baseline if stage=prod."""
    from foundation.core.registry import Registry
    from foundation.deploy.serving import deploy_to_target
    config = _load_config(args.model)
    reg = Registry(backend=config.get("registry", {}).get("backend", "local"), uri=config.get("registry", {}).get("uri", "./registry"))
    run_id = getattr(args, "version", None)
    if not run_id:
        print("Provide --version or --run-id (run_id of the run to deploy).", file=sys.stderr)
        return 1
    run_info = reg.get_run(args.model, run_id)
    run_dir = _run_dir(config, run_id)
    artifact_path = run_info.get("artifact_path") or str(run_dir / "artifact")
    metrics = run_info.get("metrics")
    deploy_to_target(args.model, run_id, artifact_path, target=args.stage, metrics=metrics, config=config)
    embedded_path = _REPO_ROOT / "deployments" / "embedded" / args.model / "model.bin"
    print(f"Deployed to deployments/embedded/{args.model}/model.bin (stage={args.stage})")
    if args.stage == "prod" and metrics:
        print("Baseline saved to baselines/ for regression protection.")
    return 0


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
    p_train.add_argument("--run-id", default=None, help="Override run ID (default: model_YYYYMMDD_HHMMSS)")
    p_train.add_argument("--data-path", default=None)
    p_train.add_argument("--dataset", default=None, help="Dataset identifier (e.g. dummy:v1)")
    p_train.set_defaults(func=cmd_train)
    # eval
    p_eval = sub.add_parser("eval")
    p_eval.add_argument("--model", required=True)
    p_eval.add_argument("--run-id", required=True)
    p_eval.add_argument("--eval-data", default=None)
    p_eval.set_defaults(func=cmd_eval)
    # register (MLflow)
    p_reg = sub.add_parser("register")
    p_reg.add_argument("--model", required=True)
    p_reg.add_argument("--run", "--run-id", dest="run_id", required=True, help="Run ID (e.g. model_YYYYMMDD_HHMMSS)")
    p_reg.add_argument("--stage", default="dev", choices=["dev", "staging", "prod"])
    p_reg.set_defaults(func=cmd_register)
    # deploy (copy to deployments/embedded)
    p_dep = sub.add_parser("deploy")
    p_dep.add_argument("--model", required=True)
    p_dep.add_argument("--version", dest="version", required=True, help="Run ID to deploy (e.g. model_YYYYMMDD_HHMMSS)")
    p_dep.add_argument("--stage", default="staging", choices=["staging", "prod"])
    p_dep.set_defaults(func=cmd_deploy)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
