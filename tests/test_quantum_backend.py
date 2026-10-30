"""Independent SF integration and honest fallback regression tests."""
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from src import gaussian_quantum as quantum


@pytest.mark.parametrize('t', [0., .1, .5, 1.])
def test_pure_loss_general_covariance(t):
    covariance = np.diag([.25, 4.])
    m, v = quantum.pure_loss([2., -.8], covariance, t)
    np.testing.assert_allclose(m, np.sqrt(t) * np.array([2., -.8]))
    np.testing.assert_allclose(v, t * covariance + (1 - t) * np.eye(2))


def test_missing_backend_preserves_api_and_rng(monkeypatch):
    monkeypatch.setenv('FOURIER_SF_PYTHON', '/nonexistent/fourier-sf-python')
    summary, arrays = quantum.validate_quantum(n=1000)
    repeat_summary, repeat_arrays = quantum.validate_quantum(n=1000)
    assert summary == repeat_summary
    assert summary['backend'] == 'exact Gaussian covariance-matrix fallback'
    assert 'FileNotFoundError' in summary['reason']
    assert 'not a Strawberry Fields execution' in summary['reason']
    assert set(arrays) == {'quantum_transmissivity', 'quantum_mean_theory',
                           'quantum_mean_empirical', 'quantum_variance_theory',
                           'quantum_variance_empirical'}
    for key, values in arrays.items():
        assert values.shape == (11,)
        np.testing.assert_array_equal(values, repeat_arrays[key])


@pytest.mark.parametrize('error', [
    subprocess.CalledProcessError(1, ['python'], stderr="ModuleNotFoundError: No module named 'pkg_resources'"),
    subprocess.TimeoutExpired(['python'], 60),
])
def test_subprocess_failures_are_evidenced(monkeypatch, error):
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(quantum.subprocess, 'run', fail)
    summary, _ = quantum.validate_quantum(n=10)
    assert type(error).__name__ in summary['reason']
    if isinstance(error, subprocess.CalledProcessError):
        assert error.stderr in summary['reason']


def test_wrong_backend_physics_is_not_silently_fallback(monkeypatch):
    records = [{'state': label, 'T': float(t), 'mean': [99., 99.],
                'covariance': np.eye(2).tolist()}
               for label in ('vacuum', 'coherent') for t in np.linspace(0, 1, 11)]
    monkeypatch.setattr(quantum.subprocess, 'run', lambda *a, **kw:
                        subprocess.CompletedProcess(a, 0, json.dumps({'records': records})))
    with pytest.raises(AssertionError):
        quantum.validate_quantum(n=10)


def test_actual_isolated_strawberry_fields(monkeypatch):
    python = Path(quantum.__file__).resolve().parents[1] / '.venv-sf/bin/python'
    if not python.exists():
        pytest.skip('Optional .venv-sf not installed; see docs/QUANTUM_BACKEND.md')
    monkeypatch.setenv('FOURIER_SF_PYTHON', str(python))
    summary, arrays = quantum.validate_quantum()
    assert summary['backend'] == 'Strawberry Fields gaussian (isolated subprocess)', summary['reason']
    assert summary['sf_states_checked'] == 22
    assert summary['sf_max_mean_error'] < 1e-10
    assert summary['sf_max_covariance_error'] < 1e-10
    assert summary['max_mean_error'] < .02
    assert summary['max_variance_error'] < .02
    np.testing.assert_allclose(arrays['quantum_variance_theory'], 1.)
    np.testing.assert_allclose(arrays['quantum_mean_theory'],
                               2 * np.sqrt(arrays['quantum_transmissivity']))


@pytest.mark.parametrize('n', [0, 1, 1.5])
def test_invalid_sample_count(n):
    with pytest.raises(ValueError, match='n must'):
        quantum.validate_quantum(n=n)
