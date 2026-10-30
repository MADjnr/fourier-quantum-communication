"""Deterministic physics tests; run with python -m unittest -v test_demo.py."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

SPEC = importlib.util.find_spec('run_demo')
if SPEC is not None:
    import run_demo as demo


class DemoTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SPEC, 'run_demo implementation must exist')
        self.g = demo.Grid()
        self.r = demo.simulate(self.g)

    def test_normalization_and_parseval(self):
        for key in ('target', 'displaced', 'aberrated', 'single', 'two', 'shift_corrected'):
            u = self.r[key]
            self.assertAlmostEqual(demo.power(u, self.g.dx), 1., places=12)
            self.assertAlmostEqual(demo.power(demo.spectrum(u, self.g), self.g.dxf), 1., places=12)
            np.testing.assert_allclose(demo.ift(demo.ft(u)), u, atol=1e-11)

    def test_shift_theorem_sign_and_fractional_displacement(self):
        ramp = self.r['ramp']
        np.testing.assert_allclose(demo.ft(self.r['displaced']), demo.ft(self.r['target']) * np.exp(-1j*ramp), atol=1e-10)
        self.assertLess(np.linalg.norm(self.r['shift_corrected']-self.r['target'])/np.linalg.norm(self.r['target']), 1e-12)
        wrong = demo.ift(demo.ft(self.r['displaced'])*np.exp(-1j*ramp))
        self.assertLess(demo.overlap(wrong, self.r['target']), .6)

    def test_phase_bound_is_attained_and_magnitude_preserved(self):
        u, t = self.r['aberrated'], self.r['target']
        bound = demo.phase_bound(u, t)
        self.assertAlmostEqual(demo.overlap(self.r['single'], t), bound, places=12)
        self.assertLess(bound, .9)
        np.testing.assert_allclose(abs(demo.ft(self.r['single'])), abs(demo.ft(u)), atol=1e-10)
        for scale in (0., .5, 1.5, 2.):
            candidate = demo.ift(demo.ft(u)*np.exp(1j*scale*self.r['single_phase']))
            self.assertLessEqual(demo.overlap(candidate, t), bound+1e-12)

    def test_two_plane_removal_recovers_complex_target(self):
        np.testing.assert_allclose(self.r['aberrated']*np.exp(1j*self.r['upstream_phase']), self.r['displaced'], atol=1e-11)
        self.assertLess(np.linalg.norm(self.r['two']-self.r['target'])/np.linalg.norm(self.r['target']), 1e-12)
        self.assertAlmostEqual(demo.overlap(self.r['two'], self.r['target']), 1., places=12)

    def test_continuum_predictions(self):
        analytic = demo.continuum(self.g)
        for name, field in [('displacement_uncorrected', 'displaced'), ('defocus_uncorrected', 'aberrated'), ('single_plane_bound', 'single'), ('two_plane', 'two')]:
            self.assertAlmostEqual(demo.overlap(self.r[field], self.r['target']), analytic[name], places=11)
        g = demo.Grid(defocus=0.)
        self.assertAlmostEqual(demo.continuum(g)['single_plane_bound'], 1., places=14)
        # One independent resolution check, not a parameter/statistical sweep.
        fine = demo.Grid(n=512, dx=6e-6)
        rf = demo.simulate(fine)
        self.assertAlmostEqual(demo.overlap(rf['single'], rf['target']), analytic['single_plane_bound'], places=11)

    def test_artifact_contract(self):
        import tempfile
        import json
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            demo.save_demo(Path(directory), self.g, self.r)
            names = sorted(p.name for p in Path(directory).glob('*.png'))
            self.assertEqual(names, ['01_optical_schematic.png', '02_displacement_only.png', '03_spectral_amplitude_limit.png', '04_correction_comparison.png'])
            metrics = json.loads((Path(directory)/'metrics.json').read_text())
            self.assertAlmostEqual(metrics['numerical']['two_plane'], 1., places=12)
            with np.load(Path(directory)/'fields.npz') as arrays:
                np.testing.assert_array_equal(arrays['two'], self.r['two'])


if __name__ == '__main__':
    unittest.main()
