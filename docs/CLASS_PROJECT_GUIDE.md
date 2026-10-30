# Classroom project guide

**Afam Madu and Tofayel Karim**

## Start here

1. Read the [class paper](../class_project/paper.pdf) ([source](../class_project/paper.tex)).
2. Present with the [four-page speaking script](../class_project/speaking-script.pdf) ([source](../class_project/speaking-script.tex)). Read the connected paragraphs aloud; bracketed directions and filenames are presenter cues. Display the corresponding figure from the paper or the PNG beside the script.
3. Inspect the [standalone demo README](../class_project/README.md), [code](../class_project/run_demo.py), and [saved metrics](../class_project/output/metrics.json) for precise conventions and checks.

No quantum or machine-learning prerequisite is assumed. The question is whether a phase plate can recover a displaced Gaussian, why defocus limits a single Fourier-plane plate, and how an upstream plate changes that limit.

## Four-figure presentation route

| Figure and file | What to point out |
|---|---|
| 1 — [`01_optical_schematic.png`](../class_project/output/01_optical_schematic.png) | Read the pale-blue boxes left to right: input, optional upstream plate, transform lens, Fourier phase plate, inverse lens/output. No quantitative axes or color scale; not to scale. The upstream plate is absent in the single-plane case. |
| 2 — [`02_displacement_only.png`](../class_project/output/02_displacement_only.png) | Three intensity images: target, displaced, corrected. x/y in mm; dark-to-pale magma colors mean increasing intensity, all divided by target peak. Fourth panel is the y=0 slice: target black dashed, displaced orange solid, corrected blue dotted. Corrected and target coincide. |
| 3 — [`03_spectral_amplitude_limit.png`](../class_project/output/03_spectral_amplitude_limit.png) | Target and aberrated **amplitudes**, not intensities; xF/yF in physical Fourier-plane mm. Purple-to-green-to-yellow means increasing amplitude divided by target spectral peak. Right yF=0 slice: target black dashed, before orange solid, after blue dotted. Before/after coincide; a phase-only plate cannot change that amplitude. The bound uses the entire 2D plane, not only the displayed slice. |
| 4 — [`04_correction_comparison.png`](../class_project/output/04_correction_comparison.png) | Four columns: target, uncorrected, best single plane, two planes. Top: intensity on the same scale as Figure 2. Middle: cyclic phase colors from −π to π radians, not brightness; low-intensity pixels are hidden. Both rows use x/y in mm. Bottom: horizontal overlap bars, orange uncorrected, blue single plane, green two planes; the dashed blue vertical line is the single-plane ceiling. |

The image crops improve readability; calculations use the full grid. Intensity agreement alone does not establish complex-field recovery. The script explains amplitude, phase, overlap, and Fourier decomposition before interpreting these panels.

## What the numbers mean

These are **deterministic known-input overlaps**, not averages or confidence intervals:

| Input | No correction | Best relevant correction |
|---|---:|---:|
| Displacement | 0.824758 | Fourier ramp: 1.000000 |
| Displacement + axis-centered defocus | 0.519545 | Single plane: 0.623926; two planes: 1.000000 |

Normalized power overlap is a classical spatial-mode power fraction. Every case conserves total power to rounding error; lower overlap is not absorption. The single-plane ceiling is attained by directly aligning Fourier phases, not by training. The upstream negative quadratic phase removes the known defocus before the Fourier transform; the positive Fourier ramp then removes displacement. Two plates at the same Fourier plane would not accomplish this amplitude redistribution.

The class model is ideal scalar lossless Fourier optics with **no imposed tilt, astigmatism, finite pupil, optimizer, quantum backend, or random ensemble**. It uses a 256×256 grid, 12 µm spacing, 1550 nm wavelength, 100 mm focal length, 220 µm field radius, displacement (90, −35) µm, and quadratic coefficient 1.4 rad. Defocus is centered on the optical axis, not the displaced beam: the spectrum both broadens and shifts. Computational boundaries are periodic, with negligible Gaussian tails for this example.

One means recovery to numerical precision for this family with exact known parameters. It does not promise hardware perfection, general correction of arbitrary aberrations, added photons, noise suppression, or communication security. No finite-aperture, plate-quantization, calibration, or unknown-jitter study is included.

## Reproduce without replacing the reference outputs

From the repository root:

```bash
cd class_project
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export MPLCONFIGDIR="$PWD/.mplconfig"
.venv/bin/python -m unittest -v test_demo.py
.venv/bin/python run_demo.py --output output_reproduced
```

The output contains exactly four PNG figures, `metrics.json`, and `fields.npz`. The six tests cover conservation and inverse transforms, the fractional shift theorem and wrong-sign control, the attainable phase-only bound, two-plane complex-field recovery, independent continuum formulas plus a resolution check, and saved-artifact integrity. See the class README for the recorded results; a resolution check is not a statistical sweep.

To rebuild only the speaking script while keeping intermediate files out of the repository:

```bash
mkdir -p /tmp/fourier-class-script-build
cd class_project # from the repository root
/tmp/fourier-paper-tools/tectonic --keep-logs \
  --outdir /tmp/fourier-class-script-build speaking-script.tex
cp /tmp/fourier-class-script-build/speaking-script.pdf speaking-script.pdf
```

The executable path above is the local delivery environment; elsewhere use an installed `tectonic`. The resulting speaking script is four A4 pages. Its PDF is a text companion, not a duplicate figure gallery.

## Keep classroom and research evidence separate

The [full research paper](../paper/main.pdf) and [full research speaking script](../paper/classroom-presentation-script.pdf) remain available as extensions. The [research paper README](../paper/README.md) supplies their reading order and build commands. The [preserved full research overview](RESEARCH_OVERVIEW.md) is the previous root README with only relative Markdown links rebased; its scientific content is retained.

The original [baseline archive](../results/) uses extra distortions and jittered train/validation/test inputs. Its 24-input mean analytic/trained overlaps, 0.469958/0.470226, are not the classroom ceiling. The separate [phase-limit investigation](../investigations/phase_limit/README.md) reports 1,280 fresh shared inputs and fixed one-/two-plane mean coupled powers 0.449020/0.948633. Those ensemble means and their uncertainty statements must not be replaced by the class values 0.623926/1.000000. The simplified demo does not rerun or revise either research evidence layer.

All versions are numerical studies, not experimental validation or externally peer-reviewed publications.
