"""
Validate datasets and payloads against data contracts.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union

from .contracts import DataContract, FieldSpec


def validate_row(row: dict[str, Any], contract: DataContract) -> list[str]:
    """Validate a single row (dict) against contract. Returns list of error messages."""
    errors = []
    for f in contract.features:
        val = row.get(f.name)
        if f.required and val is None:
            errors.append(f"Missing required field: {f.name}")
            continue
        if val is None:
            continue
        if f.allowed_values is not None and val not in f.allowed_values:
            errors.append(f"{f.name}: value not in {f.allowed_values}")
        if f.min_val is not None and (isinstance(val, (int, float)) and val < f.min_val):
            errors.append(f"{f.name}: {val} < min {f.min_val}")
        if f.max_val is not None and (isinstance(val, (int, float)) and val > f.max_val):
            errors.append(f"{f.name}: {val} > max {f.max_val}")
    if contract.target and contract.target.required:
        if contract.target.name not in row:
            errors.append(f"Missing target: {contract.target.name}")
    return errors


def validate_dataframe(df: Any, contract: DataContract) -> list[str]:
    """Validate a DataFrame-like (has .columns and .iloc). Returns list of errors."""
    errors = []
    for col in contract.feature_names():
        if col not in df.columns:
            errors.append(f"Missing column: {col}")
    if contract.target and contract.target.name not in df.columns:
        errors.append(f"Missing target column: {contract.target.name}")
    # Per-row checks can be added for dtypes/ranges
    return errors


def load_contract_from_dict(d: dict) -> DataContract:
    """Build a DataContract from a dict (e.g. from model.yaml)."""
    features = [
        FieldSpec(
            name=fd["name"],
            dtype=fd.get("dtype", "float"),
            required=fd.get("required", True),
            allowed_values=fd.get("allowed_values"),
            min_val=fd.get("min_val"),
            max_val=fd.get("max_val"),
        )
        for fd in d.get("features", [])
    ]
    target = None
    if d.get("target"):
        t = d["target"]
        target = FieldSpec(name=t["name"], dtype=t.get("dtype", "float"), required=t.get("required", True))
    return DataContract(
        name=d.get("name", "contract"),
        version=d.get("version", "1.0"),
        features=features,
        target=target,
        identifiers=d.get("identifiers", []),
    )
