#!/usr/bin/env python3
"""
Batch inference pipeline: run predictions on a dataset and write output.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-path", required=True, help="Path to model bundle")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    from foundation.core.runner import run_predict
    import pandas as pd

    df = pd.read_csv(args.input)
    result = run_predict(
        model_name=args.model,
        model_path=args.model_path,
        input_data=df,
    )
    out_df = result if isinstance(result, pd.DataFrame) else pd.DataFrame([result])
    out_df.to_csv(args.output, index=False)
    print(f"Wrote {len(out_df)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
