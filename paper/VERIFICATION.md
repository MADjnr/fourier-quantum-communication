# Manuscript verification and evidence map

## Scope and preserved baseline

The manuscript was prepared from standalone baseline `aaccd508e712404303ca68f56911e6365cbcefe3`. It introduces no new simulation results. Existing `src/`, `tests/`, `results/`, configuration files, and dependency freezes are unchanged. The source links to the baseline and explains the historical parent-workspace provenance limitation.

## Checks performed for this manuscript

- Reran `.venv/bin/python -m pytest -q`: **41 passed**, no skips, 14 dependency deprecation warnings. The isolated Strawberry Fields integration test executed.
- Reran `python3 scripts/verify_artifacts.py`: **29 archived artifacts matched byte counts and SHA-256 hashes**.
- Checked representative values, held-out means, paired Student-t intervals, calibration values, covariance errors, and loss ceilings against `results/metrics.json`.
- Independently reviewed the manuscript against implementation and saved arrays; checked mask extrema, scan extrema, and selected checkpoint `(2, 54)` against the NPZ archive.
- Checked captions against `src/plots.py`. Corrected the drafting errors that described the Fourier-plane panel as post-mask and the comparison plot as showing five cases. The final captions correctly identify the pre-mask plane and the three correction cases.
- Compiled using IEEEtran with Tectonic 0.17.0; inspected rendered pages for layout and clipping. Final PDF has **12 pages**, ten sequentially numbered figures and four tables. No overfull boxes or unresolved citations/references remain; benign underfull-box warnings remain in some justified paragraphs/table cells.
- Verified the Gaussian-quantum-information DOI metadata via Crossref. The three official software documentation URLs returned HTTP 200 (Strawberry Fields stable links redirect to latest).

These are internal numerical/editorial checks, not external scientific peer review. Author approval, affiliation information, and a selected venue's submission checklist remain outstanding.

## Claim-to-evidence mapping

| Paper material | Primary evidence |
|---|---|
| Physical Fourier normalization and Gaussian source | `src/propagation.py`, `src/modes.py`, `src/distortions.py`, `docs/PHYSICS.md` |
| Configuration and six independent distortion distributions | `results/config.json`, `src/experiment.py` |
| Objective, starts, and validation-only selection | `src/optimization.py`, `results/metrics.json` → `optimization`, NPZ learning curves |
| Representative correction / receiver table | `results/metrics.json` → `cases`, `results/tables/cases.csv` |
| Held-out performance and all paired intervals | `results/metrics.json` → `test_distribution`, `paired_test_improvements`; saved per-sample overlaps |
| Irrecoverable loss and attainable phase-only bound | `results/metrics.json` → `lossy_failure`, `src/metrics.py`, `tests/test_acceptance.py` |
| Gaussian quantum conventions and actual backend execution | `src/gaussian_quantum.py`, `results/metrics.json` → `quantum_validation`, `tests/test_quantum_backend.py` |
| Calibration, conditioning, variance, phase rotation and SNR | `src/homodyne.py`, `src/plots.py`, archived arrays and case metrics |
| Verification table | All three test modules, archived logs, optical/gradient/backend metrics, internal review documents |
| Data preservation and provenance limits | `results/manifest.json`, `docs/PUBLICATION.md`, `scripts/verify_artifacts.py` |

## Recheck without regenerating the experiment

From the repository root:

```sh
.venv/bin/python -m pytest -q
python3 scripts/verify_artifacts.py
(cd paper && tectonic --keep-logs main.tex)
```

Do not regenerate the published `results/` simply to compile the paper. New experiments should use a new `runs/` destination.
