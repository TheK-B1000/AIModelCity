"""
Common pipeline runner: load config, resolve model entrypoints, run train/eval/predict.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable, Optional


def load_model_module(model_name: str, entrypoint: str) -> Optional[Callable]:
    """Load a callable from models/<model_name>/<entrypoint>.py (e.g. train, predict, eval)."""
    models_root = Path(__file__).resolve().parent.parent.parent / "models"
    module_path = models_root / model_name / f"{entrypoint}.py"
    if not module_path.exists():
        return None
    # Ensure model package is loaded so relative imports (e.g. "from . import features") work
    parent_pkg = f"models.{model_name}"
    if parent_pkg not in sys.modules:
        importlib.import_module(parent_pkg)
    spec = importlib.util.spec_from_file_location(f"{parent_pkg}.{entrypoint}", module_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    # Convention: run_train, run_predict, run_eval
    fn_name = f"run_{entrypoint}"
    return getattr(mod, fn_name, None)


def run_train(
    model_name: str,
    config: dict,
    data_path: str,
    output_path: str,
    **kwargs: Any,
) -> dict:
    """Run model training via model's train.py."""
    run_fn = load_model_module(model_name, "train")
    if run_fn is None:
        raise RuntimeError(f"No run_train in models/{model_name}/train.py")
    return run_fn(config=config, data_path=data_path, output_path=output_path, **kwargs)


def run_predict(
    model_name: str,
    model_path: str,
    input_data: Any,
    **kwargs: Any,
) -> Any:
    """Run model prediction via model's predict.py."""
    run_fn = load_model_module(model_name, "predict")
    if run_fn is None:
        raise RuntimeError(f"No run_predict in models/{model_name}/predict.py")
    return run_fn(model_path=model_path, input_data=input_data, **kwargs)


def run_eval(
    model_name: str,
    model_path: str,
    eval_data_path: str,
    config: dict,
    **kwargs: Any,
) -> dict:
    """Run model evaluation via model's eval.py."""
    run_fn = load_model_module(model_name, "eval")
    if run_fn is None:
        raise RuntimeError(f"No run_eval in models/{model_name}/eval.py")
    return run_fn(model_path=model_path, eval_data_path=eval_data_path, config=config, **kwargs)
