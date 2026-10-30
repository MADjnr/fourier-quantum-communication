# Training-free Fourier optics classroom demo

**Question:** Why can one Fourier-plane phase plate exactly correct displacement,
but not generally displacement plus defocus? Can a second, upstream phase plate
remove that limitation for a known input?

This standalone NumPy/Matplotlib calculation answers those questions for one
Gaussian and two deterministic distortions. There is no training, optimizer,
quantum backend, statistical sweep, imposed tilt, or astigmatism. Existing research
code and evidence outside this directory are unchanged. These are numerical
ideal-optics examples, not measurements or communication/security results.

## Reproduce

From this directory, with Python 3.10 or later:

```bash
python -m venv .venv
.venv/bin/python -m pip install --no-cache-dir -r requirements.txt
export MPLCONFIGDIR="$PWD/.mplconfig"
.venv/bin/python -m unittest -v test_demo.py
.venv/bin/python run_demo.py
```

The script defaults to `output/` beside itself, regardless of the working
directory. It writes exactly four PNG figures, `metrics.json`, and `fields.npz`.
It overwrites its own named outputs when rerun; to preserve this reference run:

```bash
.venv/bin/python run_demo.py --output output_reproduced
```

Tested environment: Python 3.11.12, NumPy 2.4.6, Matplotlib 3.11.2. The requirements
list only the two direct dependencies; SciPy and pytest are unnecessary. Full
installed versions are recorded in `environment.txt`. Floating-point last digits
and PNG bytes may vary by library/platform.

## Model and conventions

The target is `u0(x,y) = C exp[-(x²+y²)/w²]`, with C chosen so the sampled
integrated power is one. Thus w is the field's 1/e radius (intensity 1/e² radius).
The displaced field is `ud = C_d exp[-((x-dx0)²+(y-dy0)²)/w²]`. The second case is

```
u(x,y) = ud(x,y) exp[i a (x²+y²)/w²].
```

The quadratic phase is centered on the **optical axis**, not on the displaced
beam. This follows `src/distortions.py`. Even with no imposed linear tilt, that
combination shifts the spectral centroid as well as broadening the spectrum;
it must not be described as a pure centered spectral broadening.

Parameters copied from `src/config.py`: wavelength 1550 nm, focal length 100 mm,
waist 220 µm, displacement (90, −35) µm, defocus a = 1.4 rad in the expression
above, spatial sample spacing 12 µm. N is increased from the repository's 128 to
256 to suppress finite-window tails: the field of view is 3.072 mm per side.
No finite pupil is imposed: this intentionally isolates the phase-only limit
from aperture loss. Neither detector losses nor channel attenuation are used.

`ft` is a centered NumPy 2D FFT with `norm='ortho'` and the negative-exponent
forward transform; `ift` is its inverse. This matches `src/propagation.py`,
including the inverse-image convention: physical relay image inversion and lens
global phase are absorbed into output coordinates. These are exact ideal focal
transforms, not a claim of a separate sampled lens/free-space propagation model.

For spatial frequency f in cycles/m, the Fourier-plane coordinate is
`xF = wavelength * focal_length * f`. Physical Fourier field samples are
`U = ft(u) * dx/dxF`, with `dxF = wavelength*focal_length/(N*dx)`.
Thus `sum(|u|²) dx² = sum(|U|²) dxF²`. The relay can use unitary array FFTs
directly because the physical forward/inverse scaling factors cancel.
The computational boundaries are periodic; Gaussian tails are negligible here.

### 1. Displacement only

The shift theorem gives `F[ud] = F[u0] exp[-i 2π(fx dx0 + fy dy0)]`.
The compensating Fourier phase is therefore **positive**:
`phi_shift = +2π(fx dx0 + fy dy0)`. Its inverse transform restores the field,
not merely its intensity. Displacements are fractional pixel offsets; we sample
the continuous shifted Gaussian rather than round to integer pixels.

### 2. Tight single-plane phase-only limit

Define normalized power overlap

```
eta = |integral conj(u0) u dx dy|² / (P0 P).
```

This is a classical spatial-mode power fraction, not a quantum fidelity or a
raw amplitude overlap. Parseval and the triangle inequality give the attainable
single-Fourier-plane ceiling

```
eta_max = (integral |U0| |U| dA_F)² / (P0 P).
phi_best = arg(U0 conj(U)).
```

The best mask aligns every Fourier component with the target phase. It leaves
`|U|` unchanged. Cauchy–Schwarz bounds the resulting magnitude overlap by one,
with equality only for proportional spectral amplitudes. The code constructs
this mask directly, including harmless arbitrary phases at zero-amplitude
samples. This is the exact known-field phase-alignment solution, not an optimized
or trained approximation. It is more general than just a displacement ramp.

### 3. Two phase planes

First apply `phi_up = -a(x²+y²)/w²` **at the input plane**, leaving the displaced
Gaussian. Then apply `phi_shift` in the Fourier plane. The upstream operation
changes the spectrum that reaches the Fourier plane, so the original fixed-input
single-plane bound no longer applies. Two phase plates in the same Fourier plane
would just add phases and would not fix the amplitude mismatch. No amplitude
mask, gain, or loss is involved.

## Independent continuum predictions

Let `D = (dx0²+dy0²)/w²`. Direct Gaussian integration on an infinite plane gives

```
eta_displaced = exp(-D)
eta_aberrated = exp[-D(1 + a²/(4+a²))] / (1+a²/4)
eta_single_max = 4(1+a²)/(2+a²)² * exp[-2a² D/(2+a²)]
eta_shift_corrected = eta_two_plane = 1.
```

For example, `|F[u]|` is a Gaussian broadened by `sqrt(1+a²)`, centered at
`f_c = a*(dx0,dy0)/(π w²)`. Integrating its product with the target spectral
amplitude yields the single-plane formula. The exponential displacement factor
in that formula is essential for the axis-centered quadratic phase. These
closed-form predictions are independent of the FFT and are tested against it.

## Results from the saved reference run

| Input / correction | Numerical eta | Continuum eta |
|---|---:|---:|
| Displacement, uncorrected | 0.8247579833029632 | 0.8247579833029628 |
| Displacement, Fourier ramp | 1.0 | 1.0 |
| Displacement + defocus, uncorrected | 0.5195453715953674 | 0.5195453715953667 |
| Displacement + defocus, best single plane | 0.6239259445257396 | 0.6239259445257389 |
| Displacement + defocus, two planes | 1.0 | 1.0 |

The directly evaluated spectral-amplitude bound is 0.6239259445257388. The largest
continuum discrepancy is 6.661338147750939e−16. Relative complex-field errors
are 4.254658972826531e−16 for displacement recovery and
4.4465354792345865e−16 for two-plane recovery. Spatial and physical Fourier powers
are one to rounding error. Values equal to one are **numerical precision**, not a
claim of physically perfect hardware.

Six unittest cases pass: normalized powers/Parseval/inverse FFT; fractional
shift theorem and wrong-sign negative control; attainable phase bound and
spectral-amplitude preservation; two-plane complex-field recovery; independent
continuum comparison and one 512×512, 6 µm resolution cross-check; and generated
artifact names, saved metrics and raw-array integrity. Tests were written first
and all failed on the missing implementation before code was added. The
resolution check is numerical validation, not a distortion or statistical sweep.
`verification.log` records the passing test run. PNG decoding and dimensions were
checked programmatically; this alone is not a visual inspection.

## Four figures — manuscript-ready semantics

1. **`output/01_optical_schematic.png`** — Conceptual ideal 4f ordering: distorted
   input, optional upstream quadratic-removal plate, forward-transform lens,
   Fourier phase plate, inverse-transform lens and output. The upstream plate is
   absent for the single-plane case. The Fourier plate is phase alignment for the
   single-plane case and a positive displacement ramp for the two-plane case.
   The lower annotation gives physical f spacings; drawing is not to scale.
2. **`output/02_displacement_only.png`** — Target, displaced input, corrected
   output intensities, followed by y=0 intensity sections. Image axes are x,y in
   mm; all intensities share the target peak normalization. Curves: target black
   dashed, displaced orange solid, corrected blue dotted. The title reports
   uncorrected and corrected power overlaps. Target/corrected traces coincide.
3. **`output/03_spectral_amplitude_limit.png`** — Target and aberrated physical
   Fourier-plane **amplitude** maps, plus yF=0 amplitude sections before/after
   optimal phase correction. Axes are Fourier-plane mm, not spatial frequencies.
   All amplitudes use the target spectral peak normalization. Curves: target
   black dashed, before orange solid, after blue dotted. Before/after curves
   coincide because a phase-only mask preserves spectral amplitude. The displayed
   ceiling is computed over the full 2D plane, not only the plotted slice.
4. **`output/04_correction_comparison.png`** — Four columns: target, uncorrected
   displacement+defocus, best single plane, two planes. Top row is output
   intensity (common target-peak scale); middle row is complex-field phase in
   radians (−π to π). Phase is hidden below 1e−4 of the target peak intensity,
   where phase is visually uninformative. Bottom bars show the three corrected/
   uncorrected overlaps, with the single-plane ceiling as a dashed line. Fields
   and overlaps refer to the same input and masks; no hidden training cases.

The field images crop to ±0.6 mm and spectral images to ±0.9 mm for readability;
all computations use the entire grid. Images display intensity and phase rather
than implying intensity alone demonstrates complex-field recovery.

## Raw data and limits

`output/fields.npz` stores complex physical spatial fields (`target`, `displaced`,
`shift_corrected`, `aberrated`, `single`, `two`), unwrapped correction phases in
radians (`ramp`, `upstream_phase`), principal-value `single_phase`, and coordinate
vectors `x_m`, `xf_m`. Arrays have row=y, column=x. Reconstruct any physical
spectrum via `spectrum(field, Grid())`. Metrics contain parameters, environment,
powers, continuum values and errors without clipping overlaps to [0,1].

The known distortion parameters are assumed exactly available. Finite apertures,
phase quantization, pixelation of actual phase plates, calibration errors,
unknown fluctuating inputs, and experimental validation are out of scope.
Two-plane recovery is proven for this known displacement-plus-quadratic-phase
family; it is **not** a universal two-plane correction theorem.
