# Classroom deliverable verification

## Scope

- `paper.pdf`: six-page classroom paper; `speaking-script.pdf`: four-page recitable companion.
- Authors preserved: Afam Madu and Tofayel Karim.
- Exactly four demo figures, in the same order in the paper and script.
- No training, imposed tilt, astigmatism, finite pupil, random jitter, or quantum backend in the class model.
- The original research paper, scripts, numerical evidence and figures remain separate and unchanged. Root documentation now leads with the classroom version; `docs/RESEARCH_OVERVIEW.md` preserves the former root overview with rebased relative links.

## Scientific checks

The negative-exponent transform, positive displacement ramp, negative upstream quadratic correction, spectral-amplitude bound and optical-axis-centered defocus are explicitly explained. The two-plane result is restricted to the known nominal input family, not arbitrary fields or noisy hardware.

Saved normalized power overlaps:

- Displacement: 0.824758 uncorrected, 1.000000 corrected.
- Displacement plus defocus: 0.519545 uncorrected, 0.623926 best single-plane, 1.000000 two-plane.

These are deterministic new class cases, not replacements for the earlier jittered research averages.

Executed checks:

```sh
class_project/.venv/bin/python -m unittest discover -s class_project -p 'test_demo.py' -v
.venv/bin/python -m pytest -q tests investigations/phase_limit/test_investigation.py
python3 scripts/verify_artifacts.py
```

All six class tests and all 49 existing tests pass. All 29 original archived artifact hashes match. The class tests check power/Parseval normalization, shift sign, amplitude preservation and attainable bound, full complex-field recovery, continuum formulas, finer sampling and saved output consistency.

## PDF build and visual review

From `class_project/`, with Tectonic installed:

```sh
tectonic paper.tex
tectonic speaking-script.tex
```

The local build used `/tmp/fourier-paper-tools/tectonic`, with temporary output directories outside the repository. Both PDFs passed text extraction, page-boundary and compiler checks. All ten rendered pages were visually inspected. An overlapping subplot layout in Figure 4 was corrected by sharing the same Matplotlib GridSpec; the demo was regenerated, six tests rerun, and the paper rebuilt. The final figure and compiled page 4 were visually rechecked with no clipping or overlap. Numerical results did not change.

Final paper PDF: 725479 bytes; SHA-256 `4f8114f75ea1446fe10d92633fa514e7c93d0a9c2a769970ab17492f62d461d4`.

Original research files retain their hashes:

- `../paper/main.tex`: `0d7ec558c5271d08ff1294510062c5b60610210b43984b7d506332034b45c5de`
- `../paper/main.pdf`: `9f1e5e169cd23334d6fa54c7cbc07976355e7d2c5d19cb53a108bdb1f49555e1`

Successful tests and ideal numerical recovery do not establish experimental performance, unknown-aberration recovery, or fabrication tolerance.
