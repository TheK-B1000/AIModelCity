# Build and showcase a small embedded model

Minimal path: **train → eval → deploy → run predictions** from the embedded copy.

---

## 1. One-shot build (train + eval + deploy)

From **ai-model-foundation**:

```bash
cd ai-model-foundation
pip install -r requirements.txt   # if not already
```

**Windows (CMD):**
```cmd
scripts\demo.cmd
```
Then deploy the run that was just created (use the printed Run ID):

```cmd
python foundation\cli.py deploy --model fraud_detector --version <RUN_ID> --stage staging
```

**PowerShell / Bash:** run `scripts/demo.sh` or `scripts/demo.ps1`, then same deploy command with the printed Run ID.

**Or step by step:**

```bash
# Train (creates runs/fraud_detector_YYYYMMDD_HHMMSS/)
python foundation/cli.py train --model fraud_detector --dataset demo

# Eval (use the Run ID from train output)
python foundation/cli.py eval --model fraud_detector --run-id fraud_detector_20260209_170159

# Deploy to embedded_models/
python foundation/cli.py deploy --model fraud_detector --version fraud_detector_20260209_170159 --stage staging
```

Replace `fraud_detector_20260209_170159` with the Run ID you got from `train`.

---

## 2. Showcase the embedded model

Run predictions using **only** the deployed artifact (no `runs/`):

```bash
python scripts/showcase_embedded.py --model fraud_detector
```

You should see:
- Which version is in staging (`deploy_meta.json`)
- A few example predictions (score and probability)

That demonstrates: the app loads `embedded_models/fraud_detector/model.bin` (and metadata) and serves inference.

---

## 3. Optional: use example_classifier

Same flow with the other example model (uses same data):

```bash
python foundation/cli.py train --model example_classifier --dataset demo
# Use printed Run ID below
python foundation/cli.py eval --model example_classifier --run-id <RUN_ID>
python foundation/cli.py deploy --model example_classifier --version <RUN_ID> --stage staging
python scripts/showcase_embedded.py --model example_classifier
```

---

## 4. “What’s in staging?”

```bash
# What’s deployed
type embedded_models\fraud_detector\deploy_meta.json   # Windows
cat embedded_models/fraud_detector/deploy_meta.json   # Mac/Linux
```

Shows: `model_name`, `version` (run_id), `stage`, `artifact_path`.
