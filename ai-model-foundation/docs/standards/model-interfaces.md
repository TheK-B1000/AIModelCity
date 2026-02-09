# Model interfaces

## Purpose

Each model package in **models/** exposes a consistent interface so the foundation runner, eval harness, and deploy layer can invoke them without model-specific branching.

## Required entrypoints

| File | Role |
|------|------|
| **model.yaml** | Config: name, version, input/output contract ref, thresholds, resources. |
| **train.py** | Entrypoint for training: reads config + data path, writes artifact (and optionally registers). |
| **predict.py** | Entrypoint for inference: loads artifact, accepts contract-shaped input, returns contract-shaped output. |
| **eval.py** | Entrypoint for evaluation: loads model + eval data, returns metrics dict (and optionally per-sample). |
| **features.py** | Feature transforms / engineering used by train and predict. |

## Signatures (conventions)

- **train**: `(config: dict, data_path: str, output_path: str, **kwargs) -> dict` (e.g. run_id, metrics).
- **predict**: `(model_path: str, input_data: Union[Path, DataFrame, dict], **kwargs) -> Union[DataFrame, dict, list]`.
- **eval**: `(model_path: str, eval_data_path: str, config: dict, **kwargs) -> dict` (metrics + optional gate results).

CLI and pipelines call these with standard args; model-specific options go in `model.yaml` or env.

## Standards

- Prefer one entrypoint per file (e.g. `run_train`, `run_predict`, `run_eval`) invoked by foundation.
- Document input/output shapes in model.yaml or in data-contracts.
