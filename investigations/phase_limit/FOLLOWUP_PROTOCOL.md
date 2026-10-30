# Reviewer-triggered controls (after primary result, before these runs)

The primary architecture comparison was frozen before evaluation. This supplement does not tune it. These are exploratory diagnostics.

1. Isolate training size: analytic initialization, learning rate 0.04, 800 steps, same 128-realization validation set (seed 1202); train on first 12 versus all 128 realizations of seed 1101. Select validation checkpoints identically.
2. Isolate run length: 100 versus 800 steps for the same 128/128 samples, initialization, learning rate, and selection rule. Recompute the analytic-initialized 800-step result to retain its mask separately from the best-of-three result.
3. Compare objectives using the common analytic initialization and 800-step runs, not overlap's best of three versus single-start competitors. Report per-realization conditional Gaussian information, not just coupled power.
4. Throughput clarification: fixed-pupil throughput is independent of Fourier mask for each input, but mean normalized overlap and mean power weight different inputs differently when their throughputs differ. Their equivalence in the primary model is due to the pupil transmitting essentially all light, not phase independence alone.
5. Check changing the distortion convention from grid-centered to beam-centered quadratic phase, keeping nominal coefficients/displacement/tilt. This explicitly changes the physical distortion model; it is not a correction to the original source.
6. Evaluate the input-plane screen alone, and inspect residual mode-diversity limits. All follow-up masks remain train/validation selected; reusing the original fresh set makes these follow-up comparisons exploratory, not new confirmatory tests.
