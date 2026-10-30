---
title: "Why the optimized Fourier mask plateaus — controlled numerical investigation"
type: research-investigation
status: numerically-verified
baseline-preserved: true
---

# Main conclusion

The dominant limitation is **spectral-amplitude mismatch imposed by putting all correction in one phase-only Fourier plane**. It is not a fundamental inability of phase-only optics to correct the beam. The input has quadratic aberration and tilt before its Fourier transform; these change spectral widths and positions. A mask in that Fourier plane can align spectral phases but cannot undo those amplitude changes. The nominal analytic mask already attains the exact single-plane ceiling.

A second phase screen at the input/image plane removes nominal tilt and quadratic phase before Fourier transformation. Keeping a Fourier-plane ramp then removes displacement. This fixed, entirely phase-only two-plane system substantially outperforms the original analytic architecture in the model.

## 1. What the original numbers mean

The quoted 0.470225929 versus 0.469958327 are **24-realization test averages**, not the nominal-field ceiling. The archived paired gain is 0.000267602 with 95% CI **[−0.001371684, +0.001906887]**: it did not establish improvement. This investigation reproduced the individual archived overlaps to within 1.2×10⁻¹⁵.

For the nominal mean-parameter input, the analytic overlap is **0.452898099**, equal to its Fourier-magnitude bound. The published optimized mask gives **0.452023122** on that same nominal input. Optimizing an ensemble may trade a little nominal performance for other inputs; there is no contradiction.

## 2. Controlled protocol and results

Primary test: **1,280 independent draws**, 256 each at seeds 1303/2303/3303/4303/5303. Shared draws pair every architecture comparison. Masks were frozen before test evaluation. The two-plane masks use the same known nominal parameters as the original analytic baseline; an additional control estimates them from 128 training samples only.

New training/validation seeds: 1101/1202, 128 samples each. The primary protocol is in `PROTOCOL.md`; reviewer-triggered matched controls, declared after the primary run, are in `FOLLOWUP_PROTOCOL.md`. The latter are exploratory and do not retune the primary architecture.

Here Q = T_opt × eta_mode is coupled optical power relative to incident unit power. At the default 3-mm pupil, transmission differs from one by less than 3.7×10⁻⁹ for the tested baseline inputs, so Q and normalized overlap agree at the displayed precision.

| Method | Fresh mean Q | Paired gain vs analytic, 95% CI |
|---|---:|---|
| Uncorrected | 0.408262 | -0.040759 [-0.041281, -0.040237] |
| One-plane analytic | 0.449020 | reference |
| Published optimized | 0.448737 | -0.000284 [-0.000403, -0.000165] |
| Retrained best of three | 0.449144 | +0.000124 [+0.000098, +0.000150] |
| Mean-power objective | 0.449146 | +0.000125 [+0.000097, +0.000153] |
| Information objective | 0.449133 | +0.000113 [+0.000090, +0.000135] |
| Adaptive one-plane oracle (bound) | 0.452322 | +0.003302 [+0.003043, +0.003561] |
| Fixed two-plane analytic | 0.948633 | +0.499613 [+0.495002, +0.504224] |
| Two planes, training-estimated means | 0.947342 | +0.498321 [+0.493391, +0.503251] |

**Primary result:** gain **0.499613**, paired 95% CI **[0.495002, 0.504224]**. Mean coupling increases by a factor **2.11267** (111.27% relative). The comparison is statistically significant for this specified simulation distribution. It is not a hardware validation or evidence that optimization beats a strong analytic correction in the expanded architecture: the winning two-plane masks are themselves analytic.

The original 24-sample mean and the fresh 1,280-sample mean differ because these are different random samples. The original artifact was reproduced rather than overwritten.

![Controlled diagnosis](output/figures/01_limit_diagnosis.png)

## 3. Exact physical ceiling

Let U = F[u], V = F[v] and P be the Fourier pupil. With normalized target mode v, the output is

\[
u_{out}=F^{-1}[P U e^{i\phi}],\qquad
Q=|\langle v,u_{out}\rangle|^2.
\]

The triangle inequality gives the tight realization-specific bound

\[
Q_{max}=\left(\int |PU||V|\,d^2q\right)^2,
\qquad
\eta_{max}=Q_{max}/\int|PU|^2\,d^2q,
\]

with the target norm understood as unity. Phase alignment phi = arg(V) − arg(PU) attains it. This is precisely the nominal analytic correction. Allowing a different ideal mask for every test input gives mean Q **0.452322**, only **0.003302** above the fixed analytic mask. No optimizer or objective restricted to this architecture can exceed this per-input oracle average on these same inputs.

The fixed analytic mask already reaches **99.270% of the adaptive single-plane bound**. Approximately **99.401% of its deficit from unity** is outside the reach of any single Fourier-plane phase adjustment on this test set. Those are budget decompositions, not additive causal percentages attributed to individual aberrations.

**The pupil is not the culprit.** At its configured radius it transmits essentially all input power. Smaller-pupil controls are retained in `output/results.json`; they must be judged using Q as well as eta to avoid confusing photon rejection with improved signal collection.

## 4. Which distortion produces the spectral mismatch?

For each transverse axis the continuum input is

\[
u(x)\propto e^{-(x-d)^2/w^2}e^{i k\theta x+i a x^2/w^2},
\quad a_x=D+A,\quad a_y=D-A.
\]

Its Fourier intensity has center q_c = k theta + 2ad/w² and variance (1+a²)/w². The reference Gaussian has center zero and variance 1/w². Thus

\[
\eta_{max}=\prod_{j=x,y}
\frac{2\sqrt{1+a_j^2}}{2+a_j^2}
\exp\left[-\frac{(k\theta_jw+2a_jd_j/w)^2}{2(2+a_j^2)}\right].
\]

This independently derived Gaussian formula agrees with the enlarged-window numerical ceiling to machine precision in the convergence check.

**Defocus is the largest isolated limitation** among the nominal distortion groups: defocus-only ceiling 0.755025, astigmatism-only 0.961275, tilt-only 0.908071, displacement-only essentially 1. Quadratic aberration plus displacement lowers the ceiling to 0.559578; adding imposed tilt lowers it to 0.452898. These effects interact and should not be summed as independent losses.

The interaction is especially important because the original model defines its quadratic phase about the *grid origin*, not about the displaced beam center. A displaced beam samples a nonzero phase gradient, producing extra spectral displacement. Changing only that physical convention to beam-centered quadratic phase raises the nominal ceiling to **0.686240**, without adding correction hardware. This is a different distortion model, not a bug fix to the original.

All 16 ablations below use common random draws for active jitter parameters. The nominal column has no jitter. Ensemble columns use 256 draws, seed 6303; removed groups have both mean and jitter set to zero, and masks are recalibrated for that model. Thus these are recalibrated-system comparisons, not frozen-controller intervention effects.

| Active distortion groups | Nominal one-plane ceiling | Ensemble fixed one plane Q | Ensemble fixed two planes Q |
|---|---:|---:|---:|
| None | 1.000000 | 1.000000 | 1.000000 |
| astigmatism | 0.961275 | 0.952401 | 0.992276 |
| defocus | 0.755025 | 0.748023 | 0.986659 |
| defocus + astigmatism | 0.711532 | 0.700707 | 0.979285 |
| tilt | 0.908071 | 0.904538 | 0.996976 |
| tilt + astigmatism | 0.889629 | 0.877969 | 0.989301 |
| tilt + defocus | 0.719134 | 0.709678 | 0.983710 |
| tilt + defocus + astigmatism | 0.686240 | 0.673514 | 0.976387 |
| displacement | 1.000000 | 0.990037 | 0.990037 |
| displacement + astigmatism | 0.891078 | 0.870496 | 0.976462 |
| displacement + defocus | 0.623926 | 0.610317 | 0.966716 |
| displacement + defocus + astigmatism | 0.559578 | 0.543041 | 0.953884 |
| displacement + tilt | 0.908071 | 0.895533 | 0.987044 |
| displacement + tilt + astigmatism | 0.736263 | 0.717396 | 0.973681 |
| displacement + tilt + defocus | 0.490083 | 0.478989 | 0.963763 |
| displacement + tilt + defocus + astigmatism | 0.452898 | 0.439067 | 0.951064 |

## 5. Optimizer and objective controls

The broad stress test ran three initializations (zero, random, analytic), extending optimization on the original 12/12 split and on a new 128/128 split. These stress tests change multiple settings and are not used to assign a causal training-size effect.

The matched supplement fixes analytic initialization, learning rate 0.04, validation seed 1202 with 128 samples, and the checkpoint rule:

- **12 versus 128 training samples**, nested draws at seed 1101, 800 steps each: validation retained the original analytic mask for 12 samples. With 128 samples, test Q increased to **0.449145615**, a small paired gain **0.000125213**, CI **[0.000097383, 0.000153042]**.
- **100 versus 800 steps**, all else identical: both select iteration 45 and produce the same mask/score. Longer training does not unlock a large improvement.
- **Mean overlap versus mean coupled power**, same 128/128 data, 800 steps and initialization: test means agree within 4×10⁻¹⁵. Phase-independent throughput alone is not enough to guarantee objective equivalence across inputs; here it holds because the default pupil transmits essentially all power for every input.
- **Conditional Gaussian information objective**, mean 0.5 log₂(1 + SNR_FACTOR Q): test Q **0.449132974**. Its actual held-out mean information is **0.583770076** bits per real quadrature use, versus **0.583778156** for overlap training. The difference is tiny and slightly negative; it provides no evidence that the overlap objective causes the physical plateau.

The archived optimized mask actually falls slightly below analytic on the larger fresh sample: paired difference **−0.000283698**, CI **[−0.000402759, −0.000164637]**. A small-data ensemble adjustment is not a reliable large physical gain. Conversely, the improved 128-sample mask does show a statistically detectable but very small benefit. Statistical significance and physical importance are different questions.

The information calculation assumes Gaussian modulation, the repository noise budget, known realization-conditioned channel gain, and phase compensation. It is not the information rate of an unknown fading mixture and is not a secret-key rate.

## 6. Proposed architecture: two conjugate phase planes

1. At the input plane (or an optically relayed image of it), apply

\[
\psi(x,y)=-k(\bar\theta_xx+\bar\theta_yy)
-\bar D(x^2+y^2)/w^2-\bar A(x^2-y^2)/w^2.
\]

2. Use the first Fourier-transforming lens.
3. At its Fourier plane, apply the displacement-canceling ramp

\[
\phi_F(X_F,Y_F)=\frac{2\pi}{\lambda f}
(\bar d_xX_F+\bar d_yY_F).
\]

4. Use the inverse-transform relay and couple into the unchanged target mode / homodyne LO.

The positive ramp sign follows the repository's negative-exponent forward FFT and inverse-image convention. Nominal displacements are +90 µm and −35 µm; nominal tilt is +0.65 and −0.25 mrad. The input screen's quadratic terms are equivalent, within this ideal thin-phase model, to orthogonal focal powers with focal lengths **46.714 mm and 140.141 mm**, plus a compensating linear phase. These could be implemented with a phase SLM or an appropriately designed cylindrical/toric corrector and steering elements. These numbers specify phase power, not a fully engineered optical layout.

At the nominal input, the architecture reaches Q **0.9999999995** on the original grid. On fresh jittered inputs it reaches **0.948633**; estimating means from the training data gives **0.947342**. The input screen alone reaches **0.794000**: the Fourier displacement correction remains useful.

Why it works: the upstream phase screen changes the spectrum *before* the Fourier-plane mask. It removes the shift/broadening that a mask acting only on Fourier phase could never change. Both screens remain phase-only; the important new freedom is their placement in different planes.

![Architecture, paired comparison, and loss budget](output/figures/02_architecture_and_controls.png)

### Incremental insertion loss

For an additional power transmission tau relative to the original architecture, Q_new = tau × Q_two_plane. Mean break-even is **tau = 0.473334**, or **3.248 dB incremental loss**.

- At **90% extra transmission**, mean Q = **0.853770**, paired gain CI **[0.400243, 0.409257]**.
- At **50% extra transmission**, mean Q = **0.474317**, paired gain CI **[0.021104, 0.029489]**.

Break-even here is for mean performance. Some individual inputs can lose after attenuation. The scalar loss model does not include pixelation, phase quantization, diffraction efficiency, alignment error, extra aberration, finite lens aperture, or bandwidth dependence; those need an engineering-stage study.

## 7. Why the two-plane result is below unity

A fixed lossless receiver cannot collapse distinct random input modes to one output mode while preserving inner products. With rho = E[|u><u|], every fixed unitary W obeys

\[
E|\langle v|W|u\rangle|^2 \le \lambda_{max}(\rho).
\]

The same unconditional coupled-power bound holds for a fixed passive contraction. On each of the five 256-input empirical ensembles, the unitary ceiling is approximately **0.94686–0.95525**, while the corresponding fixed two-plane score is **0.94483–0.95370**. These are separate finite-ensemble bounds, not a confidence interval or an asserted population bound. Jitter is now the principal residual limitation; increasing its standard deviations lowers both attainable coupling and the architecture's score.

An independent 100,000-draw continuum-formula calculation (seed 9303, no FFT) gives two-plane mean **0.949291**, CI **[0.949037, 0.949545]**, consistent with the numerical result. Further large gains toward unity would require adaptive estimation/correction, channel stabilization, or collecting/detecting multiple spatial modes—not merely more training of a fixed phase mask. Adaptive operation requires a new control/measurement and noise-budget analysis.

## 8. Verification and limitations

- **49 tests passed**: 41 original tests and 8 new tests, including power normalization, phase-bound attainment, exact nominal correction on a larger window, independent continuum formulas, direct-versus-spectral propagation, autograd finite difference, and empirical ensemble bound.
- **All 29 archived artifact hashes unchanged.** Original paper, figures, source, and result files are preserved. No GitHub commit or push was made for this investigation.
- **Grid/window convergence:** same 32 diagnostic inputs, seed 8303. Fine pitch and doubled window do not change the conclusion. The largest difference in the displayed mean one-plane scores is below 2.5×10⁻⁸. These checks cover analytic architectures and bounds, not retraining every optimized mask at each grid.

| N | Pixel pitch (µm) | Window (mm) | One-plane Q | Two-plane Q |
|---:|---:|---:|---:|---:|
| 128 | 12 | 1.536 | 0.4563987809 | 0.9370671341 |
| 256 | 6 | 1.536 | 0.4563987803 | 0.9370671340 |
| 256 | 12 | 3.072 | 0.4563987566 | 0.9370671334 |
| 512 | 6 | 3.072 | 0.4563987566 | 0.9370671334 |

- The original narrow window causes tiny continuum discrepancies (order 10⁻⁸ in the bound); doubling it reduces those diagnostics to machine precision. Mathematical identity tests therefore use the larger window rather than loosening their tolerances.
- Paired Student-t intervals estimate Monte Carlo mean uncertainty conditional on the stated Gaussian parameter distribution and frozen masks. They omit uncertainty about actual hardware, distribution parameters, and training datasets. Follow-up/ablation comparisons are exploratory with no multiplicity correction.
- This is an **ideal scalar, monochromatic FFT relay**, not lens-by-lens vector electromagnetic modeling, a fabricated-device result, an experimental validation, an observed BER improvement, or a demonstrated secure quantum link.
- Dependency output contains existing Matplotlib/Pyparsing deprecation warnings; no numerical test failures remain.

## 9. Reproduce / inspect

From the repository root, using the existing environment:

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python -m pytest -q tests investigations/phase_limit/test_investigation.py
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python investigations/phase_limit/run_study.py
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python investigations/phase_limit/run_followup.py
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python investigations/phase_limit/render_report.py
.venv/bin/python scripts/verify_artifacts.py
```

- `output/results.json`: full results, seeds, configuration, dependency versions, baseline commit and source hashes.
- `output/scores.npz`: per-input scores, parameters and seed membership, including historical reproduction.
- `output/masks.npz`, `output/followup_masks.npz`: fixed mask arrays.
- `output/optimization.json`, `output/followup.json`: validation selection, learning curves, matched controls and information results.
- `output/figures/`: PNG and SVG comparative visualizations.
- `verification.log`, `run.log`, `followup.log`: executed run logs.

**Smallest useful next experiment:** add and calibrate the input-plane quadratic/tilt corrector, retain displacement compensation at the Fourier plane, and measure *coupled power and total transmission* on the same perturbation sequence. Compare against the strongest two-plane analytic baseline before claiming a benefit from learned masks.
