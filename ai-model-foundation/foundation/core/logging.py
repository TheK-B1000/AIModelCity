"""
Structured logging for pipelines and services.
"""
from __future__ import annotations

import json
import logging
import sys
from typing import Any


def configure_logging(level: str = "INFO", structured: bool = True) -> None:
    """Configure root logger with optional JSON-structured output."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        stream=sys.stdout,
        format="%(message)s" if structured else "%(levelname)s %(name)s %(message)s",
    )


def log_structured(level: int, msg: str, **kwargs: Any) -> None:
    """Emit one structured log line (JSON)."""
    record = {"message": msg, **kwargs}
    line = json.dumps(record)
    logging.log(level, line)
