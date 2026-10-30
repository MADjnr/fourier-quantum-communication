# Quantum backend: independently executed Gaussian validation

## Environment and compatibility evidence

Strawberry Fields **successfully executes** in a separate `.venv-sf`, using
Python 3.11.12, Strawberry Fields 0.23.0, NumPy 1.26.4 and SciPy 1.11.4.
The parent `.venv` was not modified. Installation used `uv --no-config` and an
explicit PyPI index to avoid the machine's global uv index configuration.

Initial installation succeeded, but the import failed with this actual error:

```text
strawberryfields/__init__.py:24 -> from . import apps
strawberryfields/apps/__init__.py:33 -> import strawberryfields.apps.data
strawberryfields/apps/data/__init__.py:70 -> import strawberryfields.apps.data.sample
strawberryfields/apps/data/sample.py:20 -> import pkg_resources
ModuleNotFoundError: No module named 'pkg_resources'
```

Installing `setuptools==70.3.0` in **only `.venv-sf`** resolved that missing
legacy runtime dependency. No monkey patches were needed. The first installation
was bounded by `timeout 300` (resolution 15.63 s, preparation 4m05 s); the single
repair was bounded by `timeout 30` and completed in seconds. Total downloads
remained below five minutes. No further downloads were attempted.

Reproduce from the project root (the combined timeout bounds all downloads):

```sh
timeout 300 sh -c '
  uv --no-config venv --python 3.11 .venv-sf &&
  uv --no-config pip install --python .venv-sf/bin/python \
    --index-url https://pypi.org/simple \
    numpy==1.26.4 scipy==1.11.4 strawberryfields==0.23.0 setuptools==70.3.0
'
.venv/bin/python -m pytest -q tests/test_quantum_backend.py
.venv/bin/python -c 'from src.gaussian_quantum import validate_quantum; print(validate_quantum()[0])'
```

Other observed transitive versions included thewalrus 0.21.0, numba 0.68.1,
llvmlite 0.50.0 and sympy 1.14.0. This is an evidenced working installation,
not a complete transitive lockfile. `.venv-sf` is a local environment, not source
that should be committed.

## What is actually validated

`validate_quantum(seed=904, n=100000)` launches the isolated Python interpreter
with a 60-second timeout. `FOURIER_SF_PYTHON` can select another interpreter;
otherwise the project-local `.venv-sf/bin/python` is used. The worker runs an
actual `sf.Program(1)` and `sf.Engine('gaussian')` for each of 22 cases:

- Vacuum and coherent amplitude `alpha=1-0.4j`.
- Eleven transmissivities, `T=0, 0.1, ..., 1`, including both endpoints.
- `ops.Coherent` preparation (vacuum is the engine default), followed by
  `ops.LossChannel(T)`.
- Both quadrature means via `state.means()` and the entire covariance via
  `state.cov()`, explicitly with `sf.hbar=2`.

The host checks every returned mean and covariance against the exact channel
with absolute tolerance `1e-10`. A numerical mismatch raises an error rather
than concealing a failed validation as a compatibility fallback.

Observed default-run results:

```text
backend: Strawberry Fields gaussian (isolated subprocess)
sf_states_checked: 22
sf_max_mean_error: 2.220446049250313e-16
sf_max_covariance_error: 0.0
max_mean_error: 0.004502143052460756
max_variance_error: 0.00824528571471761
n_symbols: 100000
```

The last two errors are **NumPy Monte Carlo homodyne errors**, not SF errors.
The existing `(summary_dict, arrays_dict)` API, default arguments, summary keys
and five array keys are preserved. Empirical arrays remain seeded NumPy samples
of the coherent-state x quadrature, shape `(11,)`. Added `sf_*` summary fields
identify independent SF validation; we do not claim those samples were drawn
by SF.

## Exact covariance fallback

If the interpreter is missing, import/execution fails, times out, or returns
invalid JSON, the summary explicitly labels the covariance fallback and records
the exception and, for nonzero exit status, worker stderr. The fallback does
**not** claim SF execution. It keeps installations without SF usable.

For `hbar=2`, vacuum covariance is `I`, and mixing a Gaussian mode with an
independent vacuum mode on a beam splitter gives

```text
r_out = sqrt(T) r_in + sqrt(1-T) r_vac
m_out = sqrt(T) m_in
V_out = T V_in + (1-T) I
```

The vacuum has zero mean; independent inputs have zero cross-covariance.
For a coherent state `m_in=(2 Re(alpha), 2 Im(alpha))` and `V_in=I`, so variance
remains exactly one at every T. For vacuum the mean remains zero as well.
This moment propagation is mathematically equivalent to the Gaussian pure-loss
channel used by SF, not an approximation to it. NumPy Gaussian samples test
finite-sample statistics but alone would not establish independent backend
agreement. Regression tests additionally cover a squeezed input covariance,
missing interpreter, captured import error, timeout, deterministic array/API
preservation, and refusal to hide incorrect backend moments.
