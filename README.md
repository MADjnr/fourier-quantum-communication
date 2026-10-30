# Fourier optics: why one phase plate has a limit

**Afam Madu and Tofayel Karim**

Start with this **training-free classroom project**: a Gaussian light beam is displaced, then given a known defocus phase. One Fourier-plane phase plate corrects displacement exactly, but cannot generally repair a mismatch in spectral amplitude. An upstream phase plate removes the known defocus first, allowing two-plane recovery for this narrow model.

## Read and present

- **[Class paper (PDF)](class_project/paper.pdf)** · [LaTeX source](class_project/paper.tex)
- **[Recitable classroom speaking script (PDF)](class_project/speaking-script.pdf)** · [Editable source](class_project/speaking-script.tex)
- [Class project guide](docs/CLASS_PROJECT_GUIDE.md) — reading order, four figures, and evidence boundaries
- [Standalone demo and detailed model](class_project/README.md) · [Saved metrics](class_project/output/metrics.json) · [Four figures](class_project/output/)

No training or quantum background is required. The demo uses only NumPy and Matplotlib: **no optimizer, quantum backend, random distortion sweep, imposed tilt, astigmatism, or finite pupil**. It is an ideal lossless numerical example with exactly known distortions, not a hardware or communication-security demonstration.

## Main classroom results

Normalized power overlap measures how much of a normalized field matches the target spatial mode; it is not total transmitted power.

| Deterministic input | Correction | Power overlap |
|---|---|---:|
| Displacement only | None | 0.824758 |
| Displacement only | Fourier phase ramp | 1.000000 |
| Displacement + defocus | None | 0.519545 |
| Displacement + defocus | Best single Fourier plane | 0.623926 |
| Displacement + defocus | Upstream + Fourier phase planes | 1.000000 |

The single-plane result attains its spectral-amplitude ceiling. Recovery to one means numerical precision in this known-field model, not perfect real equipment or universal correction of arbitrary distortions. Defocus is centered on the optical axis; with displacement it both broadens and shifts the spectrum.

## Run the classroom demo

From the repository root, with Python 3.10 or later:

```bash
cd class_project
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export MPLCONFIGDIR="$PWD/.mplconfig"
.venv/bin/python -m unittest -v test_demo.py
# Keep the reference output unchanged:
.venv/bin/python run_demo.py --output output_reproduced
```

This produces four PNG figures, `metrics.json`, and `fields.npz`; no training is run. See the [class README](class_project/README.md) for conventions, continuum checks, and limitations.

## Full research extensions — preserved, separate evidence

The classroom project is a reduction, **not a replacement or rerun** of the original jittered research studies. Its deterministic overlaps must not be substituted for their test-set means.

- [Full research paper (PDF)](paper/main.pdf) · [Full research speaking script (PDF)](paper/classroom-presentation-script.pdf) · [Research paper guide](paper/README.md)
- [Preserved full research overview](docs/RESEARCH_OVERVIEW.md) — the previous root README, with relative links adjusted for its new location
- [Archived baseline](results/) · [Phase-limit investigation](investigations/phase_limit/README.md)

Those extensions include additional distortions, training comparisons, jittered test ensembles, and quantum-limited receiver modeling. The manuscript is not an accepted IEEE publication or externally peer-reviewed article. No experimental validation, lost-photon recovery, shot-noise reduction, or secret-key rate is claimed.

Public visibility alone does not grant an open-source license; no license has been selected yet.
