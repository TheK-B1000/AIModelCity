# Naming standards

## Repo and directories

- **Monorepo root**: `ai-model-foundation` (or project name).
- **Model packages**: `models/<model_slug>/` — lowercase, snake_case (e.g. `fraud_detector`, `churn_prediction`).

## Files

- **Config**: `model.yaml` per model; `defaults.yaml` in foundation/config.
- **Entrypoints**: `train.py`, `predict.py`, `eval.py`, `features.py` (lowercase, clear purpose).
- **Tests**: `tests/test_<module>.py` (e.g. `test_features.py`, `test_contracts.py`).

## Code and config

- **Python**: snake_case for modules, functions, variables; PascalCase for classes.
- **YAML**: kebab-case or snake_case for keys; be consistent within a file.
- **Registry / runs**: run IDs and version strings are opaque but unique; use semantic version for “model version” when promoting (e.g. `1.2.0`).

## Artifacts and deployments

- **Artifact paths**: include model name + run_id or version (e.g. `fraud_detector/v1.2.0` or `fraud_detector/<run_id>`).
- **Deployments**: name K8s resources and services after model + env (e.g. `fraud-detector-staging`, `fraud-detector-prod`).
