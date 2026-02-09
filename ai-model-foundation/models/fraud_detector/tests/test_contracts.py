"""
Tests for fraud_detector data contract validation.
"""
import pandas as pd
import sys
from pathlib import Path

# Add repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from foundation.data.contracts import load_contract_from_dict
from foundation.data.validate import validate_dataframe, validate_row


def test_validate_row_missing_required():
    contract = load_contract_from_dict({
        "name": "test",
        "features": [{"name": "amount", "dtype": "float", "required": True}],
    })
    errors = validate_row({}, contract)
    assert any("amount" in e for e in errors)


def test_validate_row_pass():
    contract = load_contract_from_dict({
        "name": "test",
        "features": [{"name": "amount", "dtype": "float", "required": True}],
    })
    errors = validate_row({"amount": 10.0}, contract)
    assert len(errors) == 0


def test_validate_dataframe_missing_column():
    contract = load_contract_from_dict({
        "name": "test",
        "features": [{"name": "amount", "dtype": "float"}],
    })
    df = pd.DataFrame({"other": [1, 2]})
    errors = validate_dataframe(df, contract)
    assert any("amount" in e for e in errors)


def test_validate_dataframe_pass():
    contract = load_contract_from_dict({
        "name": "test",
        "features": [{"name": "amount", "dtype": "float"}],
    })
    df = pd.DataFrame({"amount": [1.0, 2.0]})
    errors = validate_dataframe(df, contract)
    assert len(errors) == 0
