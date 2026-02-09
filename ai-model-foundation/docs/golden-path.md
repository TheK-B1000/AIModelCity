# Golden Path

The 6-command path from zero to a deployed model.

## 0. Bootstrap (first time only)

```bash
./scripts/bootstrap_local.sh
# or: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

## 1. Validate data

Ensure your dataset matches the model’s data contract:

```bash
foundation/cli.py validate --model fraud_detector --data path/to/dataset.csv
```

## 2. Train

Reproducible training (config from `model.yaml`, code + config recorded):

```bash
foundation/cli.py train --model fraud_detector
# or: pipelines/train_pipeline.py --model fraud_detector
```

## 3. Evaluate

Run eval harness vs baselines; gates determine pass/fail:

```bash
foundation/cli.py eval --model fraud_detector --run-id <train-run-id>
# or: pipelines/eval_pipeline.py --model fraud_detector --run-id <id>
```

## 4. Register

Artifacts and metadata are stored under **runs/<run_id>/** (see [Surveyor's Office](standards/surveyors-office.md)) and indexed in the registry. Promote to “production” when gates pass.

## 5. Deploy

Deploy to staging, then canary, then full prod:

```bash
pipelines/deploy_pipeline.py --model fraud_detector --version <version> --target staging
# then canary, then prod
```

## 6. Monitor

Observability (errors, latency, drift-lite) runs in production; see runbooks for incidents and rollback.

---

See **runbooks/** for rollback, retrain, and incident handling.
