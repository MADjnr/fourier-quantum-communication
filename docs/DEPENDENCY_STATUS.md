# Dependency status and reproducibility

Observed installed versions (not inferred from old setup pins):

| Environment | Versions |
|---|---|
| `.venv` | torch 2.5.1+cpu; torchoptics 0.4.0; NumPy 1.26.4; SciPy 1.11.4; PyYAML 6.0.3; pytest 9.2.0 |
| `.venv-sf` | StrawberryFields 0.23.0; NumPy 1.26.4; SciPy 1.11.4; setuptools 70.3.0 |

`requirements.txt` and `requirements-sf.txt` are complete exact freezes of these installed environments, produced by `uv --no-config pip freeze --python .venv/bin/python` and the corresponding `.venv-sf` command. The setup script uses Python 3.11.12 and syncs the exact requirements; CPU torch is available from the explicit PyTorch CPU index. These are version locks, not hashed wheel or platform-independent reproducibility guarantees. A clean-machine reinstall has not been performed during this remediation.

SF runs in a subprocess to avoid mixing its dependencies with the optical engine. Setuptools 70.3.0 retains pkg_resources required by the SF dependency stack. SF validates vacuum and coherent pure-loss moments on an 11-point transmissivity grid. The caller records successful backend/version evidence or an actual subprocess failure before falling back to exact covariance. Physics disagreement from a working backend raises rather than falling back. NumPy generates empirical homodyne samples separately.

Report-only preserves the simulation manifest and creates a render manifest; no claim about current environment availability is substituted for archived backend identity. Historical manifests may contain older package versions and must not be rewritten to match current locks. See REFERENCES.md for official API URLs, checked with curl (HTTP 200).
