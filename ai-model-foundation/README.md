# AI Model Foundation (v1)

This repo is our **AI Model Foundation**: a repeatable system to **build, train, test, register, and deploy models** with consistent gates and traceability.

If you can run 6 commands, you can ship a model.

---

## What you can do here

- **Validate** datasets against model-specific data contracts
- **Train** — reproducible run ID `model_YYYYMMDD_HHMMSS`, artifact under `runs/<run_id>/artifact/` (model.bin, model.joblib)
- **Eval** — baseline gates; exit code **12** on failure (CI blocks promotion)
- **Register** — MLflow Registry Hall (`foundation register --model X --run <run_id> --stage dev|staging|prod`)
- **Deploy** — copy to `embedded_models/<model>/model.bin`; prod deploy saves baseline to `baselines/`
- Monitor basic health (errors, latency, drift-lite)

---

## Golden Path (the 6 commands)

### 0) Bootstrap (first time only)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/bootstrap_local.sh
foundation/cli.py train --model fraud_detector
```

See [docs/golden-path.md](docs/golden-path.md) for the full workflow. **Build & showcase an embedded model:** [docs/build-and-showcase-embedded.md](docs/build-and-showcase-embedded.md). Repo conventions: [docs/standards/surveyors-office.md](docs/standards/surveyors-office.md). **Phase 1 (MLflow, gates, deploy):** [docs/phase1-checklist.md](docs/phase1-checklist.md).

---

## Demo (one-shot validate → train → eval)

**Prereqs:** Python 3.10+, `pip install -r requirements.txt` (pandas, pyyaml, scikit-learn, joblib).

**Unix (Git Bash / WSL / macOS/Linux):**
```bash
cd ai-model-foundation
./scripts/demo.sh
```

**Windows (CMD or PowerShell):**
```cmd
cd ai-model-foundation
scripts\demo.cmd
```
*(If you prefer the PowerShell script and get an execution-policy error, run once: `powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1`.)*

**Or step by step:**
```bash
cd ai-model-foundation
python foundation/cli.py validate --model fraud_detector --data data/train.csv
python foundation/cli.py train --model fraud_detector
# Use the printed Run ID in the next command:
python foundation/cli.py eval --model fraud_detector --run-id <RUN_ID>
```
