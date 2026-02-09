# AI Model Foundation (v1)

This repo is our **AI Model Foundation**: a repeatable system to **build, train, test, register, and deploy models** with consistent gates and traceability.

If you can run 6 commands, you can ship a model.

---

## What you can do here

- Validate datasets against model-specific data contracts
- Train models in a reproducible way (dataset + code + config recorded)
- Evaluate vs baselines with required gates
- Register model artifacts and metadata
- Deploy to staging/prod with canary and rollback
- Monitor basic health signals (errors, latency, drift-lite)

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

See [docs/golden-path.md](docs/golden-path.md) for the full workflow. Repo conventions, naming, and run structure: [docs/standards/surveyors-office.md](docs/standards/surveyors-office.md).

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
