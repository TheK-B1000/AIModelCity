#!/usr/bin/env bash
# Bootstrap local environment for AI Model Foundation (venv + deps)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "Bootstrap at $REPO_ROOT"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "Created .venv"
fi

# Activate (allow shell to source this script for activation)
if [ -f ".venv/Scripts/activate" ]; then
  . .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
  . .venv/bin/activate
fi

pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
else
  pip install pyyaml pandas scikit-learn joblib
fi

echo "Done. Activate with: source .venv/bin/activate (Unix) or .venv\\Scripts\\activate (Windows)"
