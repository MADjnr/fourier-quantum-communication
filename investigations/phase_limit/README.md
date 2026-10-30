# Single-plane ceiling and two-plane correction investigation

**Start with [REPORT.md](REPORT.md)** for the derivation, complete tables, two figures, and limitations. This is new numerical evidence alongside—not a replacement for—the [original archive](../../results/report.md).

## What changed scientifically?

The nominal analytic one-plane overlap **0.452898099** is the attainable spectral-amplitude ceiling, not a failed optimization. A phase mask in that Fourier plane cannot change spectral magnitudes. Input-plane tilt and quadratic phase have already shifted and broadened those magnitudes. The archived **0.469958 / 0.470226** numbers are instead averages over 24 jittered inputs.

A fixed input/image-plane phase screen removes mean tilt and curvature before Fourier transformation; a fixed Fourier-plane ramp then corrects mean displacement. On 1,280 fresh shared inputs, analytic one-plane mean coupled power is **0.449020**, the per-input adaptive one-plane bound is **0.452322**, and fixed analytic two-plane coupling is **0.948633**. The paired two-minus-one gain is **0.499613**, 95% CI **[0.495002, 0.504224]**. This is an architecture result, not learned superiority. Both masks remain phase-only; spectral magnitudes change because the upstream correction acts in a different plane.

Coupled power `Q = T_opt × eta_mode` is relative to incident unit power. The baseline pupil transmits essentially all power. For extra transmission `tau`, compare `tau × Q_two_plane` with the original architecture, not normalized overlap alone. Mean break-even is **tau = 0.473334**; no insertion loss was measured.

The new matched controls find only a tiny one-plane training gain, while fixed-receiver performance remains limited by jitter. Neither a confidence interval nor an empirical ensemble bound establishes hardware performance, arbitrary-channel robustness, BER, or a secure key rate.

## Publication checks

The integrated manuscript and six-page speaking companion were rebuilt and visually checked. The combined suite passes 49 tests, and all 29 original archived artifacts retain their recorded hashes. For publication, the local repository path in `verification.log` was replaced by `<repo>` and only that log's manifest entry was refreshed; numerical arrays, figures, and scientific results were not changed.

## Evidence map

| Question | Read / inspect |
|---|---|
| What was declared before the primary run? | [PROTOCOL.md](PROTOCOL.md) |
| Which later controls are exploratory? | [FOLLOWUP_PROTOCOL.md](FOLLOWUP_PROTOCOL.md) |
| Primary statistics, configuration, seeds, source hashes | [output/results.json](output/results.json): `fresh`, `paired_q_vs_analytic`, `nominal`, `grids`, `empirical_unitary_bounds` |
| Matched training/objective controls and loss budget | [output/followup.json](output/followup.json): `matched`, `paired_q`, `information_bits_per_real_quadrature_use`, `budget` |
| Per-input paired data and fixed masks | [output/](output/): `scores.npz`, `followup_scores.npz`, `masks.npz`, `followup_masks.npz` |
| Validation checkpoint selection | [output/optimization.json](output/optimization.json), `followup.json → records` |
| Comparative images and panel meanings | [output/figures/](output/figures/), [figure guide](../../docs/FIGURE_GUIDE.md) |
| Executed verification and file inventory | [verification.log](verification.log), [MANIFEST.json](MANIFEST.json) |
| Classroom explanation | [speaking script PDF](../../paper/classroom-presentation-script.pdf) |

Load numerical archives with `numpy.load(path, allow_pickle=False)`. The report's preservation statements describe the investigation run before subsequent manuscript/document integration; the original `results/` evidence remains unchanged, while reader-facing paper and companion documents are updated separately.

## Verify without regenerating evidence

From the repository root, with the existing project environment:

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python -m pytest -q tests investigations/phase_limit/test_investigation.py
python3 scripts/verify_artifacts.py
```

The recorded combined suite has **49 passing tests** (41 original plus 8 investigation tests). Original artifact verification covers **29 archived hashes**, not every file in the expanded repository.

## Reproduce without overwriting the retained investigation

The investigation runners and renderer use paths relative to their own directory; they do **not** offer the baseline runner's `--output` option. Running them in place overwrites retained outputs (the renderer also rewrites `REPORT.md`). Copy the investigation scripts to a fresh two-level directory under the repository so their repository-root discovery still works:

```sh
mkdir -p runs/phase_limit_reproduction
cp investigations/phase_limit/*.py runs/phase_limit_reproduction/
cp investigations/phase_limit/*PROTOCOL.md runs/phase_limit_reproduction/
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python runs/phase_limit_reproduction/run_study.py
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python runs/phase_limit_reproduction/run_followup.py
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python runs/phase_limit_reproduction/render_report.py
```

Choose an unused destination for each run. The scripts read the original baseline and write new outputs in the copied directory. Preserve the original protocols alongside any changed experimental design. Reproduction can take substantially longer than simply reading the evidence.
