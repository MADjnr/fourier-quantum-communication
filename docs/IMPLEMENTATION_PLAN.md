# Fourier quantum communication implementation plan

Goal: execute stages 0–6 of the root Linux specification without modifying existing research documents.
Architecture: sampled unitary 4f FFT relay with TorchOptics Field/phase elements and independent NumPy oracle; torch ensemble optimization; NumPy homodyne and Gaussian backend validation; static publication figures/report.
Tech: local uv Python 3.11, CPU torch, TorchOptics, scipy/numpy/matplotlib, pytest.
No commits or system changes. Execute directly in this delegated task.

## Stage 0
1. Inspect host/repo; record commands and official documentation/API.
2. Create pinned requirements and scripts/setup_linux.sh, local .venv; test imports.
3. Attempt Strawberry Fields in isolated local .venv-sf and record evidence; use explicit covariance fallback only on demonstrated incompatibility.
## Stage 1 (TDD)
4. Write tests/test_optics.py for FFT roundtrip, NumPy agreement, Gaussian Fourier scaling, energy, overlap and clipping; run RED.
5. Implement src/optics.py; run GREEN. Use physical dx-weighted Field normalization and Fourier-plane dx_F=lambda*f/(N*dx).
6. Test distortion and phase-only bounds, gradient finite differences; implement distortions and masks.
## Stage 2 (TDD)
7. Test reproducible split ensembles and optimization improvement against nominal spectral-phase conjugate baseline.
8. Implement src/optimization.py, train 3 mask initializations on independent fixed training/validation ensembles, choose validation best, evaluate untouched test ensemble. Save every curve/mask.
## Stages 3–5 (TDD)
9. Write tests/test_quantum.py: phase rotation, pure loss covariance, Monte Carlo confidence intervals, zero modulation, reproducibility, no double-counting.
10. Implement src/quantum.py; sample >=100000 symbols per principal case and loss-validation point. Save confidence intervals, loss budget, SNR and classical mutual information, not secret-key rate.
## Stage 6 (TDD)
11. Write integration/output contract tests before CLI/plotting: ten PNG/SVG pairs, eight caption points, tables and reports.
12. Implement src/run.py and src/plots.py, baseline.yaml, report generation.
13. Execute full pipeline; rerun tests including artifact validation. Save numerical validation and runtime logs.
14. Write PHYSICS, REFERENCES, FIGURE_GUIDE, FABRICATION_ROADMAP and README with actual commands, limitations and next experiments.

## Verification
Run `.venv/bin/python -m pytest -q` after each stage, retaining RED and GREEN logs under results/logs. Full run: `MPLBACKEND=Agg .venv/bin/python -m src.run --config configs/baseline.yaml`. Check all finite outputs, bounds, figure DPI and report links. Test held-out gains honestly; amplitude loss remains unrecoverable. CPU 128 grid baseline, independent 256-grid check. Exact implementation may consolidate suggested modules while retaining all required physics and outputs.
