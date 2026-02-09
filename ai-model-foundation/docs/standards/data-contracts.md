# Data contracts

## Purpose

Data contracts define the **schema and invariants** for inputs (training data, inference requests) and outputs (predictions, eval results). They are the single source of truth for validation.

## Where they live

- **Schema definitions**: foundation/data/contracts.py (and model-specific overrides in `model.yaml` or model code).
- **Validation logic**: foundation/data/validate.py.

## Contract contents

- **Features**: names, types (numeric, categorical, datetime, etc.), allowed ranges or enums.
- **Target** (if supervised): name, type, optional constraints.
- **Identifiers**: columns used for join or id (e.g. `transaction_id`).
- **Optional**: nullability, defaults, docstrings for downstream docs.

## Usage

- **Training**: validate training/validation datasets before train.
- **Serving**: validate incoming request payloads (and optionally response shape).
- **Eval**: validate eval dataset and model outputs against contract.

## Standards

- Use the same contract for train and serve where possible (feature parity).
- Version contracts when you add/remove or change features; record version in model metadata.
