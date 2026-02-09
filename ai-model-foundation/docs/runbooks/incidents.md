# Incidents runbook

## Overview

This runbook covers how to detect, triage, and respond to incidents involving model serving, data, or pipelines.

## Detection

- **Observability**: foundation/observability/monitor.py — errors, latency, drift-lite, KPIs.
- **Alerts**: Configure alerts on error rate, latency p99, and (if available) drift or accuracy proxies.
- **Reports**: Dashboards or logs from the serving layer and eval history.

## Triage

1. **Scope**: One model or many? One environment (staging/prod) or all?
2. **Symptom**: High errors, high latency, wrong predictions, missing data?
3. **Recent changes**: Last deploy, last data refresh, config change?

## Response

| Symptom | Action |
|--------|--------|
| Bad predictions / accuracy drop | Consider **rollback** (see rollback.md). Then investigate data/code and plan **retrain** (see retrain.md). |
| High latency / timeouts | Scale or resource tuning; check infra (K8s, Docker). If model-specific, consider rollback. |
| High error rate (5xx, crashes) | Check logs and deploy health; rollback if deploy-related. Fix and redeploy. |
| Data issues (missing, wrong schema) | Fix data pipeline and contract; validate and retrain if needed. |

## Post-incident

- Document: what happened, root cause, action taken (rollback, retrain, config change).
- Update runbooks or alerts if a new failure mode was found.
- Optional: create a short post-mortem and share with the team.
