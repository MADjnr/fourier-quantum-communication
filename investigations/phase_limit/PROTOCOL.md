# Controlled phase-limit investigation

## Scope (declared before new evaluation)

Preserve the published `results/`, paper, and presentation script. Use the existing ideal scalar sampled relay, source normalization, Gaussian parameter distribution, wavelength, pupil, and phase-compensated receiver assumptions. New findings are numerical, not experimental.

## Hypotheses and controls

1. **Single-plane physical ceiling:** evaluate the per-realization Fourier-magnitude overlap bound and attain it with an adaptive analytic phase. This is an oracle upper bound, not a deployable fixed mask.
2. **Optimizer/objective:** compare the archived mask, nominal analytic mask, longer optimization, increased training data, mean coupled-power objective, and mean Gaussian mutual information. Throughput is phase-independent for a fixed Fourier pupil, so mean overlap and mean coupled power should nearly coincide here. Assess absolute performance against the physical ceiling, not only optimizer wins.
3. **Distortion model:** all 16 presence/absence combinations of displacement, tilt, defocus, and astigmatism, with analytic masks recalculated for each model. Sweep jitter scales 0, 0.5, 1, 2, 4. Do not assign additive causal percentages where interactions exist.
4. **Architecture:** add a phase screen in the input/image plane to remove the known nominal tilt/quadratic phase, retaining a Fourier-plane screen to undo nominal displacement. Compare fixed analytic two-plane correction with the same fixed single-plane analytic baseline; explicitly budget incremental insertion loss.
5. **Residual diversity:** compute the largest eigenvalue of the input ensemble density operator (via its Gram matrix). This bounds mean coupled power for any fixed passive linear single-output receiver on that empirical ensemble, not population performance or adaptive correction.

## Statistical protocol

- Historical set: 24 realizations, seed 303; reproduction only, not a fresh test.
- New optimization training/validation: 128/128 realizations, seeds 1101/1202.
- Primary fresh test: 5 independent seeds 1303, 2303, 3303, 4303, 5303, 256 realizations each (1280 total), fixed before results.
- Architecture masks use configured population means, not test-fitted parameters. A training-estimated-mean control checks reliance on known parameters.
- Select learned masks using validation only. Primary architecture comparison: paired two-plane minus fixed one-plane analytic coupled power. Report paired Student-t confidence interval and seed-block means; other comparisons exploratory.
- Distribution sweeps and grid checks use fixed seeds and are separately labeled diagnostics, not retuning of the primary architecture.

## Verification

Test unity power, nominal two-plane correction, single-plane bound attainment, continuum Gaussian bound agreement, ensemble eigenvalue bound, differentiable objective, and baseline reproduction. Check both finer real-space pitch and larger window. Save per-realization parameters/scores, masks, metadata, code hashes, and figures. Evaluate normalized overlap and coupled power separately; assess extra-screen loss break-even.
