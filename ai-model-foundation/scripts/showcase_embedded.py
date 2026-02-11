#!/usr/bin/env python3
"""
Showcase: load the embedded deployment model and run a few predictions.
Run from repo root:  python scripts/showcase_embedded.py [--model fraud_detector]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main():
    parser = argparse.ArgumentParser(description="Run predictions with the deployed embedded model")
    parser.add_argument("--model", default="fraud_detector", help="Model name (default: fraud_detector)")
    args = parser.parse_args()

    embedded_dir = REPO_ROOT / "deployments" / "embedded" / args.model
    if not embedded_dir.exists():
        print(f"No embedded model at {embedded_dir}. Run:", file=sys.stderr)
        print("  foundation train --model fraud_detector", file=sys.stderr)
        print("  foundation deploy --model fraud_detector --version <RUN_ID> --stage staging", file=sys.stderr)
        return 1

    deploy_meta_file = embedded_dir / "deploy_meta.json"
    if deploy_meta_file.exists():
        meta = json.loads(deploy_meta_file.read_text())
        print(f"Embedded model: {meta.get('model_name')} (version: {meta.get('version')}, stage: {meta.get('stage')})")
        print()

    from foundation.core.runner import run_predict

    # Example inputs (same schema as fraud_detector: amount, merchant_id, hour)
    examples = [
        {"amount": 25.0, "merchant_id": "m_a", "hour": 14},
        {"amount": 1200.0, "merchant_id": "m_c", "hour": 2},
        {"amount": 8.0, "merchant_id": "m_b", "hour": 20},
    ]
    print("Predictions (score=1 means fraud, probability in [0,1]):")
    print("-" * 50)
    for i, row in enumerate(examples, 1):
        out = run_predict(args.model, str(embedded_dir), row)
        if isinstance(out, dict):
            print(f"  {i}. amount={row['amount']}, merchant={row['merchant_id']}, hour={row['hour']}")
            print(f"     -> score={out.get('score')}, probability={out.get('probability', 0):.3f}")
        else:
            print(f"  {i}. {out}")
    print("-" * 50)
    print("Done. This is the model currently in deployments/embedded/ (staging).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
