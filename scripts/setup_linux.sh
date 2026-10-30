#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || { printf '%s\n' 'Install uv first; system Python will not be modified.' >&2; exit 1; }
# Frozen tested environments; sync removes unlisted packages in these local venvs.
uv --no-config venv --python 3.11.12 .venv
uv --no-config pip sync --python .venv/bin/python --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match requirements.txt
uv --no-config venv --python 3.11.12 .venv-sf
uv --no-config pip sync --python .venv-sf/bin/python --index-url https://pypi.org/simple requirements-sf.txt
# requirements-sf.txt pins setuptools==70.3.0: SF dependencies require pkg_resources.
.venv/bin/python -c 'import torch, torchoptics, numpy, matplotlib, yaml; print("Imports OK; torch", torch.__version__, "CUDA", torch.cuda.is_available())'
.venv-sf/bin/python -c 'import strawberryfields as sf; print("SF", sf.__version__)'
.venv/bin/python -c 'from src.gaussian_quantum import _sf_reference; result, error = _sf_reference(); assert result is not None, error; print("SF Gaussian validation OK")'
