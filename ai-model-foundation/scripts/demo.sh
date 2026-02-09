#!/usr/bin/env bash
# Demo: validate → train → eval (run from repo root)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
echo "=== AI Model Foundation demo (from $(pwd)) ==="
echo ""

echo "1. Validate data against contract..."
python foundation/cli.py validate --model fraud_detector --data data/train.csv
echo ""

echo "2. Train..."
RUN_ID=$(python foundation/cli.py train --model fraud_detector 2>&1 | tee /dev/stderr | sed -n 's/.*Run ID: \([a-f0-9]*\).*/\1/p')
if [ -z "$RUN_ID" ]; then
  RUN_ID=$(ls -t runs 2>/dev/null | head -1)
fi
echo "   Run ID: $RUN_ID"
echo ""

echo "3. Evaluate (gate pass/fail)..."
python foundation/cli.py eval --model fraud_detector --run-id "$RUN_ID"
echo ""

echo "4. Run directory (runs/<run_id>/...):"
ls -la "runs/$RUN_ID/" 2>/dev/null || true
ls -la "runs/$RUN_ID/artifact/" 2>/dev/null || true
echo ""
echo "=== Demo done ==="
