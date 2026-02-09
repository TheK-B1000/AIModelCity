"""
Data contracts: schema definitions and optional checks.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class FieldSpec:
    """Spec for a single field (feature or target)."""
    name: str
    dtype: str  # e.g. float, int, str, category, datetime
    required: bool = True
    allowed_values: Optional[List[Any]] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None


@dataclass
class DataContract:
    """Schema + invariants for inputs or outputs."""
    name: str
    version: str = "1.0"
    features: List[FieldSpec] = field(default_factory=list)
    target: Optional[FieldSpec] = None
    identifiers: List[str] = field(default_factory=list)

    def feature_names(self) -> List[str]:
        return [f.name for f in self.features]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "features": [
                {
                    "name": f.name,
                    "dtype": f.dtype,
                    "required": f.required,
                    "allowed_values": f.allowed_values,
                    "min_val": f.min_val,
                    "max_val": f.max_val,
                }
                for f in self.features
            ],
            "target": (
                {
                    "name": self.target.name,
                    "dtype": self.target.dtype,
                    "required": self.target.required,
                }
                if self.target else None
            ),
            "identifiers": self.identifiers,
        }
