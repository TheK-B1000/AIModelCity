# Retrain runbook

## When to retrain

- Scheduled refresh (e.g. weekly/monthly).
- Data drift or performance degradation detected by observability.
- New features or contract changes.
- Post-incident (e.g. after rollback, fix data/code then retrain).

## Pre-requisites

- Data contract and datasets validated.
- Code and config changes (if any) reviewed and merged.

## Steps

1. **Prepare data**  
   Export/generate training and validation datasets. Ensure they pass contract validation:
   ```bash
   foundation/cli.py validate --model <model_name> --data <train_data>
   ```

2. **Run training pipeline**  
   ```bash
   pipelines/train_pipeline.py --model <model_name>
   ```
   Or via CLI:  
   `foundation/cli.py train --model <model_name>`

3. **Run evaluation**  
   ```bash
   pipelines/eval_pipeline.py --model <model_name> --run-id <train_run_id>
   ```

4. **Promote only if gates pass**  
   If eval gates fail, do not deploy; fix data/code and retrain.

5. **Deploy via deploy pipeline**  
   Follow golden path: staging → canary → prod. See **deploy** runbook and **rollback.md** if issues arise.

## Notes

- Always record run_id and dataset version in registry for reproducibility.
- Retrain runbooks can be automated in CI (e.g. scheduled train + eval; manual or gated deploy).
