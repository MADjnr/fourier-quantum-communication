# Figure guide

All ten figures are built from the saved experiment arrays and metrics, in headless Agg, with ≥300 dpi PNG and vector SVG. Each generated report supplies: question; variables/units; controls; actual observed values; mechanism; falsification; limitations; fabrication implications. No conclusion that optimization wins is hard-coded.

1. **Architecture:** annotated sampled 4f operator, LO branch, field-to-Gaussian boundary and actual configured wavelength/focal length. Schematic, not ray tracing.
2. **Fields:** source, pre-mask Fourier plane, optimized detector intensity and phase. Common intensity limits; distinct physical coordinates; low-intensity phase masked.
3. **Comparison:** distorted/no mask, analytic and optimized detector maps. Residual is phase relative to LO after removing the global overlap phase; dark-region phase is masked.
4. **Mask:** wrapped optimized phase and all-pixel histogram. Outside-pupil values have no optical effect. No fabrication-ready height map is implied.
5. **Learning:** training and held-out validation curves for every initialization, plus min/max envelopes (not confidence intervals). Independent test statistics are printed in the report.
6. **Robustness:** fixed-mask overlap versus x displacement and defocus; identical [0,1] color range across methods. Other aberrations held fixed; no retuning at each point.
7. **Homodyne:** unconditional densities, separately labelled latent residuals, and genuine conditional Bob-Y histograms selecting archived |Alice X| ≤ 0.1√VA, with bin counts. Gaussian overlays describe unconditional Y and residual only, not finite conditional bins. Sixth panel pairs prepared Alice X with selected Bob Y for at most 3000 regularly subsampled symbols: one-quadrature ensemble, not simultaneous X/P heterodyne. Uncompensated phase leaves P contributions.
8. **Variance:** empirical/theory unconditional nominal-SNU variances and approximate 95% Gaussian sample-variance CI; vacuum reference at 1. Lower unconditional variance can simply mean lower signal.
9. **SNR:** theoretical dB SNR versus actual overlap, and separate throughput/channel/detector/overlap/product budget. Points need not lie on one curve because throughput differs; zero SNR uses a floating-point floor.
10. **Quantum validation:** covariance theory and NumPy Monte Carlo coherent-state mean/variance against pure-loss transmissivity. The caption dynamically discloses archived SF execution or fallback; SF independently checks moments, not the plotted Monte Carlo samples.

The list above uses **archived asset numbering**, not manuscript numbering: paper figures 7–10 use assets 10, 07, 08, 09. The first ten PNG/SVG pairs remain unchanged. To re-render without modifying archived evidence, first copy `results/` into an unused `runs/` directory and run `python -m src.run --output runs/your_copy --report-only`. HTML needs its relative figure directory.

## New investigation figures (paper figures 11–12)

These separate [PNG/SVG figures](../investigations/phase_limit/output/figures/) are rendered at 180 dpi PNG plus SVG; the ≥300 dpi statement above applies only to the original ten. Their source is [render_report.py](../investigations/phase_limit/render_report.py); read [safe reproduction instructions](../investigations/phase_limit/README.md) before running it because it rewrites the investigation report and images.

### 11. Why optimization plateaus: a single Fourier plane cannot reshape its spectrum

Asset: [`01_limit_diagnosis.png`](../investigations/phase_limit/output/figures/01_limit_diagnosis.png).

- **A:** horizontal bars compare mean coupled power Q on the same 1,280 fresh held-out inputs; black whiskers are 95% intervals for each mean, **not paired-gain intervals**. Gray is uncorrected, blue analytic one plane, purple learned one plane, orange adaptive one-plane bound, teal fixed analytic two planes. Q is dimensionless incident-power fraction. The orange bound allows a different mask for each realization.
- **B:** nominal one-plane overlap ceilings after removing distortion groups, with no jitter. Defocus is the largest isolated limitation; displacement alone can be corrected. The combinations interact, so bars are not additive causal loss contributions. The full report also includes recalibrated ensemble ablations.
- **C:** Fourier horizontal coordinate in mm versus normalized x-marginal intensity in 1/mm. Blue target, red distorted, dashed teal after input-plane correction. The corrected nominal spectrum matches the target: phase applied *upstream* removes spectral broadening and shift. This is a nominal enlarged-window diagnostic, not an averaged test spectrum.
- **D:** multiplier on all jitter standard deviations versus mean Q for an independent 256-input diagnostic ensemble. Compare fixed one/two-plane scores with the adaptive one-plane and empirical fixed-unitary ceilings. Bounds are not learned masks; the empirical unitary curve is not a population confidence band.

### 12. Architecture change: correct phase before the Fourier plane, then recenter the beam

Asset: [`02_architecture_and_controls.png`](../investigations/phase_limit/output/figures/02_architecture_and_controls.png).

- **Top schematic:** input/image-plane removal of mean tilt and quadratic phase, Fourier transform, displacement-canceling Fourier ramp, then inverse relay to the fixed target/LO. Both masks are fixed; no per-input adaptation or optical gain.
- **A:** single-plane Q horizontally, two-plane Q vertically; each dot uses one shared distortion. The dashed diagonal is equal performance. These are numerical coupled powers, not measured receiver samples.
- **B:** extra two-plane power transmission horizontally, paired mean Q gain vertically; shaded approximate pointwise 95% intervals. Mean break-even is 0.473334 transmission, not a guarantee for every input or a measured component specification.
- **C:** tiny single-plane paired mean gains in units of 10⁻⁴. Matched training sizes, iteration counts, and objective controls are exploratory follow-ups. Increasing training data gives a small benefit; 100 and 800 steps select the same checkpoint. Information training does not outperform overlap training on held-out conditional information. There are no uncertainty bars in this panel; consult JSON/report intervals.
- **D:** five independent seed blocks (256 inputs each) horizontally and mean Q/bound vertically. Two planes remain close to each block's empirical unitary ceiling. The five ceiling values are finite-ensemble bounds, **not** a confidence interval.

All panels are ideal scalar simulations. The new two-plane gain is an analytic architecture improvement, not proof that learned correction is best. Original homodyne plots have not been regenerated for the new architecture.
