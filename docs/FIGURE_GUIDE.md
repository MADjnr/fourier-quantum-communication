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

Re-render using `python -m src.run --output results --report-only`. Caption numbers are recomputed from the archived arrays/metrics. HTML embeds relative PNG paths and links to SVG, so retain the figure directory with the report. No browser, display server, or network is needed for rendering.
