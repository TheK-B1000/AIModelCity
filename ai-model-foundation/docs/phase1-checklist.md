# Phase 1 Checklist (Embedded Models)

## Definition of Done

- [x] **foundation train** produces a reproducible artifact
- [x] **foundation eval** enforces baseline gates (exit code 12 on failure)
- [x] **foundation register** — MLflow shows versioned models
- [x] **foundation deploy** — copies artifact to `embedded_models/<model>/model.bin`
- [x] Baseline compare: eval loads from `baselines/<model>.json`; deploy to prod saves baseline
- [x] CI runs validate → train → eval; eval failure fails the pipeline

## "What model is in staging and why?"

Check:

```bash
cat embedded_models/<model_name>/deploy_meta.json
```

Contains: `model_name`, `version` (run_id), `stage`, `artifact_path`.

Or in MLflow UI (http://127.0.0.1:5000): Models → &lt;model&gt; → version in stage "Staging".

## Commands

| Command | Purpose |
|--------|--------|
| `foundation validate --model X --data path` | Validate data against contract |
| `foundation train --model X [--dataset dummy:v1]` | Train; run_id = `X_YYYYMMDD_HHMMSS` |
| `foundation eval --model X --run-id <run_id>` | Eval; exit 12 if gates fail |
| `foundation register --model X --run <run_id> --stage dev` | Register in MLflow (requires `mlflow ui`) |
| `foundation deploy --model X --version <run_id> --stage staging` | Copy to embedded_models; prod saves baseline |

## Run layout (Phase 1)

```
runs/<model>_YYYYMMDD_HHMMSS/
  artifact/
    model.joblib
    model.bin
    metadata.json
  meta.json
  metrics.json
  params.json
```

## STEP 0 — Registry Hall (MLflow)

```bash
cd ai-model-foundation
pip install -r requirements.txt   # includes mlflow
mlflow ui
# Open http://127.0.0.1:5000
```

Set in `foundation/config/defaults.yaml` (or env) when using MLflow:

```yaml
registry:
  backend: mlflow
  uri: http://127.0.0.1:5000
```

Then train will log runs to MLflow; register will create model versions and set stage.
