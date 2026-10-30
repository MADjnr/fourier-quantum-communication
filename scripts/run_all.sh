#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export MPLBACKEND=Agg
PYTHON="${PYTHON:-.venv/bin/python}"
"$PYTHON" -m pytest -q
"$PYTHON" -m src.run --config configs/baseline.yaml "$@"
