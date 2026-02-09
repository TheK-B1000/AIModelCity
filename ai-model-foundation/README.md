# AI Model Foundation (v1)

Repeatable system to **build, train, test, register, and deploy** models with consistent gates and traceability.

## Layout

- **docs/** — Architecture, golden path, standards, runbooks, templates
- **foundation/** — Platform SDK + CLI (registry, artifacts, runner, data contracts, eval, deploy, observability)
- **models/** — Per-model packages (e.g. `fraud_detector` with `model.yaml`, train/predict/eval)
- **pipelines/** — Orchestration entrypoints (train, eval, deploy, batch infer)
- **infra/** — Docker, K8s, CI
- **scripts/** — Local bootstrap and utilities

## Quick start

```bash
./scripts/bootstrap_local.sh
foundation/cli.py train --model fraud_detector
```

See [docs/golden-path.md](docs/golden-path.md) for the full workflow.
