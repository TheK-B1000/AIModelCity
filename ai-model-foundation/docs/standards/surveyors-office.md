# Surveyor's Office — Repo conventions, naming, run structure

Single source of truth for how we lay out the repo, name things, and structure runs.

---

## Repo conventions

- **Monorepo**: One repo for foundation SDK, all models, pipelines, infra, and docs.
- **Paths**:
  - `foundation/` — platform SDK and CLI; do not put model-specific logic here.
  - `models/<model_slug>/` — one directory per model (see naming below).
  - `pipelines/` — orchestration entrypoints only; they call foundation + model code.
  - `infra/` — Docker, K8s, CI.
  - `docs/` — architecture, golden path, standards, runbooks, templates.
- **Config**: Foundation defaults in `foundation/config/defaults.yaml`; per-model overrides in `models/<model>/model.yaml`.
- **Tests**: Per-model tests live in `models/<model>/tests/`; run from repo root with that path.

---

## Naming

- **Model slugs**: lowercase, snake_case (e.g. `fraud_detector`, `churn_prediction`).
- **Python**: snake_case for modules, functions, variables; PascalCase for classes.
- **Config keys**: snake_case in YAML (e.g. `train_path`, `gate_delta_min`).
- **Run IDs**: Opaque unique IDs (e.g. short UUID). Use semantic version (e.g. `1.2.0`) only when promoting a “released” model version.

---

## Run structure (runs/<run_id>/...)

Every training or evaluation run writes under a **single run directory** so one run = one place on disk.

- **Root**: `runs/` (config key: `runs.root`, default `./runs`).
- **Per run**: `runs/<run_id>/`
  - `runs/<run_id>/artifact/` — model bundle (e.g. `model.joblib`, `metadata.json`). This is the path used for eval, deploy, and rollback.
  - `runs/<run_id>/metrics.json` — run metrics (optional but written by train pipeline).
- **Registry**: The registry (e.g. `./registry`) is an index: it maps `(model_name, run_id)` to `artifact_path` (pointing at `runs/<run_id>/artifact`). It does not replace the run directory; it points into it.

So: **run directory standard is `runs/<run_id>/...`** with the bundle under `runs/<run_id>/artifact/`.

---

## References

- **Data contracts**: [data-contracts.md](data-contracts.md)
- **Model interfaces**: [model-interfaces.md](model-interfaces.md)
- **Naming details**: [naming.md](naming.md)
