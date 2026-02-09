# Architecture (1-pager)

## Overview

The AI Model Foundation is a monorepo that provides a **platform SDK** (foundation/) and **orchestration pipelines** (pipelines/) so each model (models/) can be built, evaluated, registered, and deployed in a consistent way.

## Components

| Layer | Purpose |
|-------|--------|
| **foundation/** | Shared SDK: registry (MLflow/simple DB), artifacts, runner, data contracts, eval harness, deploy/rollback, observability |
| **models/** | One directory per model: `model.yaml`, `train.py`, `predict.py`, `eval.py`, `features.py`, tests |
| **pipelines/** | Entrypoints that wire foundation + model: train, eval, deploy, batch infer |
| **infra/** | Docker, K8s serving, CI (e.g. GitHub Actions) |

## Data flow

1. **Data** → validated against **data contracts** (foundation/data).
2. **Train** → runner loads config from `model.yaml`, runs `train.py`, saves bundle via **artifacts** and **registry**.
3. **Eval** → **eval harness** runs `eval.py` and metrics vs **baselines**; gates decide promote/fail.
4. **Deploy** → **serving** + **canary** + **rollback** (foundation/deploy).
5. **Observe** → **monitor** (drift-lite, KPIs, errors, latency).

## Principles

- **Contract-first**: schemas and checks before training/serving.
- **Reproducibility**: dataset + code + config recorded with each run.
- **Gated promotion**: eval gates and canary before full prod.
