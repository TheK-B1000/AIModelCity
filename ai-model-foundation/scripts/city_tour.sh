#!/usr/bin/env bash
# City tour: validate → train → eval → deploy → showcase (full demo of what the foundation can do)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
echo "=== City tour: what this foundation can do ==="
echo ""

echo "1. Validate (data contracts)..."
python foundation/cli.py validate --model fraud_detector --data data/train.csv
echo ""

echo "2. Train (reproducible run)..."
OUT=$(python foundation/cli.py train --model fraud_detector --dataset demo 2>&1)
echo "$OUT"
RUN_ID=$(echo "$OUT" | sed -n 's/.*Run ID: \([^,]*\).*/\1/p' | tr -d ' ')
[ -z "$RUN_ID" ] && RUN_ID=$(ls -t runs 2>/dev/null | head -1)
echo "   Run ID: $RUN_ID"
echo ""

echo "3. Eval (gates)..."
python foundation/cli.py eval --model fraud_detector --run-id "$RUN_ID"
echo ""

echo "4. Deploy (embedded_models)..."
python foundation/cli.py deploy --model fraud_detector --version "$RUN_ID" --stage staging
echo ""

echo "5. Showcase (predict from embedded model only)..."
python scripts/showcase_embedded.py --model fraud_detector
echo ""

echo "6. What's in staging?"
cat embedded_models/fraud_detector/deploy_meta.json 2>/dev/null || true
echo ""
echo "=== City tour done ==="
