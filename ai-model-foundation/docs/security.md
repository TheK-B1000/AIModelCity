# Security

Security baseline for the AI Model Foundation and how to harden it as you add AI and APIs.

---

## Immediate (do this week)

### 1. Dependencies

- **Pinned versions:** `requirements.txt` uses exact versions. Regenerate with:
  `pip install pip-tools && pip-compile requirements.in -o requirements.txt`
- **Audit:** CI runs `pip-audit -r requirements.txt` and fails on known vulnerabilities. Fix or document exceptions.

### 2. Secrets

- **No secrets in repo.** Audit every config file (`model.yaml`, `defaults.yaml`, etc.) for API keys, DB URLs, or credentials. Use environment variables or a secret manager.
- **`.env.example`** lists placeholder env vars. Copy to `.env` locally; never commit `.env`. Required vars are documented in the README.

### 3. Data paths

- **`data/*.csv`** (and similar) are in `.gitignore`. Real data must not be committed.
- Pull production data from secure storage at runtime; pass paths via `--data-path` or config. Document where real data lives in your runbooks.

### 4. Artifact integrity

- **Checksums:** When writing artifacts to `runs/<run_id>/artifact/` and when copying to `deployments/embedded/`, we generate a **SHA-256** checksum (`checksum.sha256`). At load time (`load_bundle`), the checksum is verified; a tampered model is rejected with a clear error.

### 5. Deploy directory lockdown

- **Write access:** Only the CI/deploy pipeline (or designated automation) should write to `deployments/embedded/`. Restrict write permission at the OS or IAM level so that the serving app and ad-hoc users cannot modify deployed artifacts.
- **Serving app:** Runs with **read-only** access to `deployments/embedded/` so a compromised app cannot replace the model.

---

## Short-term (next 2 weeks)

### 6. Eval gate (exit 12)

- The eval gate is **non-optional.** A model that fails eval must not be promoted to staging or production.
- **Bypass:** Bypassing the gate (e.g. deploying a model that failed eval) requires a **formal, written exception** with sign-off (e.g. security + ML owner). Document the process; no one should be able to push a failing model to production without that exception.

### 7. Provenance metadata

- When you train, we record **provenance** in `runs/<run_id>/meta.json` and `params.json`: `git_commit`, `git_branch`, `dataset`, `data_path`, `run_id`. When you register a model, this gives you a full trace from the deployed model back to code and data.

### 8. Access control

- Define **who can run** train, eval, register, and deploy. In a team setting, only CI service accounts should deploy to staging/prod. Use branch protection so that only reviewed code triggers the pipeline.

### 9. Logging

- **Audit logging:** Do not log full data rows, raw payloads, or anything that could contain PII. Log `run_id`, model name, and high-level metrics only. See `foundation/core/logging.py` and any custom logging in models.

### 10. Retention policy for `runs/`

- Set up a **cron job or script** to archive or delete runs older than N days so you are not accumulating stale copies of data and models. Document N and the process in a runbook.

---

## When you add inference APIs

### 11. Auth and rate limiting

- Every endpoint that serves predictions or triggers pipeline actions must have **authentication**, **role-based authorization**, and **rate limiting**. Monitor for unusual query patterns that could signal model extraction attempts.

### 12. Network isolation

- Put training and inference behind a **private network**. Expose only what is necessary through a gateway with WAF and rate limiting.

### 13. If you add LLMs

- Treat **all user input in prompts as untrusted.** Separate system and user segments. Validate/sanitize model outputs before they touch any downstream system (DB, APIs, other agents). **Never put secrets in prompts.**

---

## Checklist summary

| Area | Status |
|------|--------|
| Pinned deps + pip-compile | ✅ requirements.txt pinned; requirements.in for regen |
| pip audit in CI | ✅ Fails on known vulns |
| No secrets in repo; .env.example | ✅ Documented; .env.example present |
| data/*.csv in .gitignore | ✅ |
| Artifact checksum (SHA-256) | ✅ Save/load/deploy; verify at load |
| Deploy dir write restriction | Document; enforce via OS/IAM |
| Eval gate non-optional | Document; formal exception for bypass |
| Provenance (git, dataset) | ✅ In meta.json / params.json |
| Access control | Document; branch protection + CI-only deploy |
| Logging (no PII) | Document; audit code |
| Retention for runs/ | Document; add script/cron |
| API auth + rate limit | When you add APIs |
| Network isolation | When you add APIs |
| LLM prompt/output safety | When you add LLMs |
