"""Pure-loss reference and isolated Strawberry Fields Gaussian validation (hbar=2)."""
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np


def pure_loss(mean, covariance, transmissivity):
    if not 0 <= transmissivity <= 1:
        raise ValueError('Transmissivity outside [0,1]')
    mean = np.asarray(mean, float)
    covariance = np.asarray(covariance, float)
    return (np.sqrt(transmissivity) * mean,
            transmissivity * covariance + (1 - transmissivity) * np.eye(len(mean)))


def _sf_worker():
    """Executed only by the isolated interpreter; never import SF into the host."""
    import scipy
    import strawberryfields as sf
    from strawberryfields import ops

    sf.hbar = 2
    records = []
    for label, alpha in [('vacuum', 0j), ('coherent', 1 - .4j)]:
        for t in np.linspace(0, 1, 11):
            program = sf.Program(1)
            with program.context as q:
                if label == 'coherent':
                    ops.Coherent(abs(alpha), np.angle(alpha)) | q[0]
                ops.LossChannel(float(t)) | q[0]
            state = sf.Engine('gaussian').run(program).state
            records.append({'state': label, 'T': float(t),
                            'mean': state.means().tolist(),
                            'covariance': state.cov().tolist()})
    return {'versions': {'python': sys.version.split()[0], 'numpy': np.__version__,
                         'scipy': scipy.__version__, 'strawberryfields': sf.__version__},
            'records': records}


def _sf_reference():
    python = os.environ.get('FOURIER_SF_PYTHON') or str(
        Path(__file__).resolve().parents[1] / '.venv-sf' / 'bin' / 'python')
    try:
        result = subprocess.run([python, str(Path(__file__).resolve()), '--sf-worker'],
                                capture_output=True, text=True, timeout=60, check=True)
        payload = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        detail = str(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            detail += '\n' + exc.stderr.strip()
        return None, f'{type(exc).__name__}: {detail}'
    # A functioning backend that disagrees with physics must fail, not silently fall back.
    records = payload['records']
    if len(records) != 22:
        raise ValueError('Strawberry Fields returned an incomplete validation grid')
    mean_errors, covariance_errors = [], []
    for record, (label, t) in zip(records, ((label, t) for label in ('vacuum', 'coherent')
                                            for t in np.linspace(0, 1, 11))):
        if record['state'] != label or record['T'] != t:
            raise ValueError('Strawberry Fields validation grid mismatch')
        expected_m, expected_v = pure_loss([0., 0.] if label == 'vacuum' else [2., -.8],
                                          np.eye(2), t)
        m, v = np.asarray(record['mean']), np.asarray(record['covariance'])
        if m.shape != (2,) or v.shape != (2, 2):
            raise ValueError('Strawberry Fields returned invalid moment dimensions')
        np.testing.assert_allclose(m, expected_m, atol=1e-10, rtol=0)
        np.testing.assert_allclose(v, expected_v, atol=1e-10, rtol=0)
        mean_errors.append(float(np.max(abs(m - expected_m))))
        covariance_errors.append(float(np.max(abs(v - expected_v))))
    payload['max_mean_error'] = max(mean_errors)
    payload['max_covariance_error'] = max(covariance_errors)
    return payload, None


def validate_quantum(seed=904, n=100000):
    """Return the original (summary, arrays) API, plus explicit backend evidence.

    Empirical arrays remain seeded NumPy homodyne samples. SF independently
    validates both quadrature means and the full covariance for 22 states.
    """
    if not isinstance(n, (int, np.integer)) or n < 2:
        raise ValueError('n must be an integer >= 2')
    sf_result, failure = _sf_reference()
    ts = np.linspace(0, 1, 11)
    means, variances, measured, measured_var = [], [], [], []
    rng = np.random.default_rng(seed)
    for t in ts:
        m, v = pure_loss([2., -.8], np.eye(2), t)
        samples = rng.multivariate_normal(m, v, size=n)
        means.append(m[0])
        variances.append(v[0, 0])
        measured.append(samples[:, 0].mean())
        measured_var.append(samples[:, 0].var(ddof=1))
    summary = {
        'backend': ('Strawberry Fields gaussian (isolated subprocess)' if sf_result else
                    'exact Gaussian covariance-matrix fallback'),
        'reason': ('SF Gaussian engine validated vacuum and coherent pure-loss moments; '
                   'empirical homodyne arrays are seeded NumPy samples.' if sf_result else
                   'SF unavailable: ' + str(failure) + '\nUsing exact hbar=2 covariance channel '
                   'V_out=T V_in+(1-T) I; this is not a Strawberry Fields execution.'),
        'max_mean_error': float(np.max(abs(np.array(means) - measured))),
        'max_variance_error': float(np.max(abs(np.array(variances) - measured_var))),
        'n_symbols': n,
    }
    if sf_result:
        summary.update(sf_versions=sf_result['versions'], sf_states_checked=22,
                       sf_max_mean_error=sf_result['max_mean_error'],
                       sf_max_covariance_error=sf_result['max_covariance_error'])
    return summary, {'quantum_transmissivity': ts, 'quantum_mean_theory': np.array(means),
                     'quantum_mean_empirical': np.array(measured),
                     'quantum_variance_theory': np.array(variances),
                     'quantum_variance_empirical': np.array(measured_var)}


if __name__ == '__main__':
    if sys.argv[1:] != ['--sf-worker']:
        raise SystemExit('Internal worker: use --sf-worker')
    print(json.dumps(_sf_worker()))
