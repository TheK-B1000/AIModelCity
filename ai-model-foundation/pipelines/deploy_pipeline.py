#!/usr/bin/env python3
"""
Deploy pipeline: deploy a model version to staging or prod (with optional canary/rollback).
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
    parser.add_argument("--version", required=True)
    parser.add_argument("--target", default="staging", choices=["staging", "prod"])
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    import yaml
    from foundation.core.registry import Registry
    from foundation.deploy.serving import deploy_to_target
    from foundation.deploy.rollback import rollback_to_version

    config_path = _REPO_ROOT / "models" / args.model / "model.yaml"
    config = yaml.safe_load(config_path.read_text()) or {} if config_path.exists() else {}
    defaults = _REPO_ROOT / "foundation" / "config" / "defaults.yaml"
    if defaults.exists():
        def_cfg = yaml.safe_load(defaults.read_text()) or {}
        for k, v in def_cfg.items():
            if k not in config:
                config[k] = v

    if args.rollback:
        rollback_to_version(args.model, args.version, config=config)
        print(f"Rolled back {args.model} to {args.version}")
        return 0

    reg = Registry(uri=config.get("registry", {}).get("uri", "./registry"))
    run = reg.get_run(args.model, args.version)
    artifact_path = run.get("artifact_path") or str(Path(config.get("artifacts", {}).get("root", "./artifacts")) / args.model / args.version)
    deploy_to_target(args.model, args.version, artifact_path, target=args.target, config=config)
    print(f"Deployed {args.model}@{args.version} to {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
