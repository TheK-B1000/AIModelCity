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

**Or step by step:** see [docs/build-and-showcase-embedded.md](docs/build-and-showcase-embedded.md).

---

## City tour — best commands to show what this can do

Run from **ai-model-foundation** (after `pip install -r requirements.txt`). Use the **Run ID** printed by train in the next two commands.

| Step | Command | What it shows |
|------|--------|----------------|
| 1. Validate | `python foundation/cli.py validate --model fraud_detector --data data/train.csv` | Data contracts work |
| 2. Train | `python foundation/cli.py train --model fraud_detector --dataset demo` | Reproducible run → `runs/<run_id>/` with artifact, meta, metrics, params |
| 3. Eval | `python foundation/cli.py eval --model fraud_detector --run-id <RUN_ID>` | Gates pass/fail (exit 12 if fail) |
| 4. Deploy | `python foundation/cli.py deploy --model fraud_detector --version <RUN_ID> --stage staging` | Copy to `embedded_models/` |
| 5. Showcase | `python scripts/showcase_embedded.py --model fraud_detector` | Predictions from embedded model only |
| 6. What’s in staging? | `type embedded_models\fraud_detector\deploy_meta.json` (Windows) or `cat embedded_models/fraud_detector/deploy_meta.json` (Mac/Linux) | Version and stage of deployed model |

**One-shot demo (no deploy/showcase):**  
`scripts\demo.cmd` (Windows) or `./scripts/demo.sh` (Unix) — validate → train → eval.

**Full tour (validate → train → eval → deploy → showcase):**  
`scripts\city_tour.cmd` (Windows) or `./scripts/city_tour.sh` (Unix).
