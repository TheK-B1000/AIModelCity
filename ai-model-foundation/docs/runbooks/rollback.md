# Rollback runbook

## When to rollback

- Eval gates fail in production (e.g. accuracy drop, spike in errors).
- Canary shows worse KPIs than baseline.
- Critical incident (e.g. latency/timeouts, wrong predictions).

## Pre-requisites

- Registry has a previous **production** version for the model.
- Deploy pipeline and foundation/deploy/rollback support version pinning.

## Steps

1. **Identify current prod version**  
   Check registry or K8s deployment for the active model version.

2. **Identify last known good version**  
   From registry or run history; prefer the version that passed eval and canary before current.

3. **Run rollback**  
   ```bash
   pipelines/deploy_pipeline.py --model <model_name> --version <last_good_version> --target prod --rollback
   ```
   Or use foundation CLI:  
   `foundation/cli.py deploy rollback --model <model_name> --to-version <version>`

4. **Verify**  
   - Check serving endpoint health and sample predictions.  
   - Confirm observability (errors, latency) return to normal.

5. **Communicate**  
   Notify stakeholders; create/post-incident note if needed.

## Rollback script

See **foundation/deploy/rollback.py** for the programmatic rollback helper used by the pipeline.
