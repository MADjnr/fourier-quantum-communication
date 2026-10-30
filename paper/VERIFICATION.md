# Manuscript verification and evidence map

## Integrated scope and preserved baseline

The revised manuscript integrates the saved `investigations/phase_limit/` study into the abstract, introduction, results, discussion, and conclusion. It preserves the original ten baseline figures and their original representative/24-input numbers; two unchanged investigation figures are added as Figs. 11–12. Original homodyne figures are explicitly not two-plane receiver simulations. The fresh 1,280-input comparison is separate from the original 24-input result.

Only `paper/main.tex`, `paper/main.pdf`, and this verification file were edited by the manuscript integration worker. No original results, investigation evidence, simulation source, or figure files were regenerated or edited. No commit or push was performed. Other concurrent publication edits belong to separate workers.

The original manuscript source export was `aaccd508e712404303ca68f56911e6365cbcefe3`; the investigation records baseline `2c681a6e1bfb62a06a7bdc0a94037b15f309080f`. These are distinct provenance points, not interchangeable simulation identifiers.

## Checks executed for this revision

- Read the investigation report, primary results JSON, matched follow-up JSON, and figure-rendering source. Captions distinguish marginal mean intervals from paired-gain intervals, diagnostic versus primary ensembles, nominal ablations, and finite-ensemble bounds versus population confidence intervals.
- Reran `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python -m pytest -q tests investigations/phase_limit/test_investigation.py`: **49 passed**, no skips, **14 existing Matplotlib/Pyparsing deprecation warnings**. Test log: `/tmp/fourier-manuscript-verification/tests.log` (local, not a repository artifact).
- Reran `.venv/bin/python scripts/verify_artifacts.py`: **29 archived artifacts match byte counts and SHA-256 hashes**.
- Compiled with **Tectonic 0.17.0**, actual IEEEtran class, from `paper/`. Final PDF: **16 pages, 12 sequential figure captions, five tables**. `pdfimages -list` confirms all 12 image assets are embedded, with investigation images on PDF pages 12 and 13.
- Extracted text with `pdftotext -layout`; verified original 0.469958/0.470226 and new 0.449020/0.948633 values, the [0.495002, 0.504224] paired interval, loss break-even 0.473334, and matched information value 0.583770076. Captions run 1–12 and tables I–V.
- Inspected final build stdout and TeX log: **no overfull boxes, unresolved references/citations, missing-character warnings, or TeX errors**. Benign underfull boxes remain. The log also reports TU/ptm font-shape substitutions during class initialization; the PDF builds successfully. No claim of typographic certification is made.
- Bounding-box extraction finds **no text words outside any PDF page**; every page contains text. The XML-like Poppler output required stripping control characters before parsing. PyMuPDF was unavailable in the default interpreter, so structural checks used Poppler instead. This revision was checked through extracted text, embedded-image enumeration, and page bounds; a new visual page-by-page review was not performed.
- `git diff --check -- paper/main.tex` passed.

These are internal numerical/editorial checks, not external scientific peer review or experimental certification. Author approval and venue-specific submission checks remain outstanding.

## Claim-to-evidence mapping

| Paper material | Primary evidence |
|---|---|
| Physical normalization and Gaussian distortions | `src/propagation.py`, `src/modes.py`, `src/distortions.py`, original `results/config.json` |
| Original representative optical/homodyne results | `results/metrics.json` → `cases`, `results/tables/cases.csv` |
| Original 24-input means and paired intervals | `results/metrics.json` → `test_distribution`, `paired_test_improvements`; investigation `results.json` → `historical`, `historical_original_paired`, `reproduction_max_abs_error` |
| Tight spectral-magnitude ceiling and nominal attainment | `src/metrics.py`; investigation `output/results.json` → `nominal`, `fresh.adaptive_one_plane_oracle`; `core.py` and investigation tests |
| Defocus/tilt/displacement interactions and all 16 ablations | Investigation `output/results.json` → `factorial`; `REPORT.md`; continuum formula in `core.py` |
| Fresh paired two-plane 0.449020 → 0.948633 and CI | Investigation `output/results.json` → `fresh`, `paired_q_vs_analytic`, `seed_means`; saved `output/scores.npz` |
| Matched training size, iterations, and objective comparisons | `FOLLOWUP_PROTOCOL.md`, `output/followup.json` → `matched`, `paired_q`, information summaries and training histories; `output/results.json` objective scores |
| Fixed two-plane calibration and training-estimated means | `core.py`, `output/masks.npz`, `output/results.json` → `parameter_estimate`, `fresh.two_plane_estimated` |
| Jitter and fixed-unitary/passive-contraction bound | `output/results.json` → `jitter`, `empirical_unitary_bounds`; investigation tests |
| Insertion loss, pupil, and sampling checks | `output/results.json` → `paired_q_vs_analytic`, `loss_break_even`, `pupil`, `grids`; `output/followup.json` → `budget` |
| Independent 100,000-draw continuum calculation | `output/results.json` → `independent_continuum_mc` |
| New figure captions/panel semantics | `investigations/phase_limit/render_report.py`; unchanged `output/figures/01_limit_diagnosis.png` and `02_architecture_and_controls.png` |
| Original quantum moments, noise, and calibration | `src/gaussian_quantum.py`, `src/homodyne.py`, `src/plots.py`, original metrics and backend tests |
| Original artifact integrity | `results/manifest.json`, `scripts/verify_artifacts.py` |

All investigation paths in the table are relative to `investigations/phase_limit/` unless explicitly qualified. Paired intervals are conditional Monte Carlo uncertainty, not hardware uncertainty. Follow-up/ablation comparisons are exploratory and unadjusted for multiplicity. Analytic two-plane improvement is not learned superiority, an observed BER improvement, a noise-reduction claim, or a secret-key rate.

## Exact build and inspection commands

From `paper/`, the build used a temporary output directory to avoid changing repository logs/intermediates:

```sh
mkdir -p /tmp/fourier-manuscript-verification
/tmp/fourier-paper-tools/tectonic --keep-logs \
  --outdir /tmp/fourier-manuscript-verification main.tex \
  > /tmp/fourier-manuscript-verification/build.stdout 2>&1
cp /tmp/fourier-manuscript-verification/main.pdf main.pdf
pdftotext -layout main.pdf /tmp/fourier-manuscript-verification/main.txt
pdfinfo main.pdf
pdfimages -list main.pdf
```

Final compilation log: `/tmp/fourier-manuscript-verification/main.log`. The old `paper/main.log` was not updated and is not the log for this revision. With Tectonic on PATH, the ordinary documented build remains `tectonic --keep-logs main.tex` from `paper/`.

From the repository root, repeat numerical checks without regenerating evidence:

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python -m pytest -q \
  tests investigations/phase_limit/test_investigation.py
.venv/bin/python scripts/verify_artifacts.py
```

Do not rerun experiment/render scripts into archived evidence directories merely to compile the manuscript. Investigation evidence must accompany the source for the two added relative image paths to resolve.
