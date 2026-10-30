# Final code-quality review

## Verdict: APPROVED

No critical or important blocking defects found for the documented, local, CPU baseline and ideal sampled Fourier-relay model. This is a bounded code review, not certification of apparatus convergence, security, or fabrication readiness. Specification acceptance is separately recorded in `SPEC_REVIEW.md`.

## Scope and verification

Inspected numerical propagation, Fourier sampling, mode normalization, phase masks, optical metrics, optimization/checkpoint selection, distortion sampling, homodyne statistics, isolated quantum-backend execution, configuration, CLI/artifact provenance, plots/reports, setup/run scripts, pinned dependencies, and all three test modules.

Independently executed:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
bash -n scripts/setup_linux.sh scripts/run_all.sh
```

- **41 tests passed, no skips, 14 dependency deprecation warnings, 2.96 seconds.** The real isolated Strawberry Fields test ran; TorchOptics API and independent numerical-reference tests passed.
- Independently checked all **29** artifacts listed in the saved simulation manifest: no SHA-256 mismatches.
- Loaded the saved NPZ with `allow_pickle=False`: no nonfinite arrays.
- Recomputed each saved optical throughput from detector-field intensity and physical sampling; checked each total-efficiency product against its four factors. All agreed.
- Saved quantum evidence identifies actual isolated Strawberry Fields Gaussian execution, not fallback.

## Assessment

- Physical Fourier-plane scaling and detector-plane normalization agree with the independent Gaussian transform, NumPy propagation, and power tests. Throughput and normalized overlap are kept separate.
- The actual optimization objective includes the pupil and output normalization, has a meaningful finite-difference check, and agrees with an independent detector-plane calculation. Training supplies gradients, validation selects checkpoints, and test samples are not used for selection.
- Homodyne sampling uses independent spawned streams, a single shot-noise contribution, and a separate vacuum calibration. Phase handling and the distinction between matched-quadrature and original-Alice-X mutual information are explicit.
- Quantum validation uses a bounded, isolated subprocess without a shell. Unavailable-backend failures are disclosed; successfully returned but physically wrong moments raise instead of quietly passing through fallback.
- Reports distinguish theoretical SNR from oracle latent-component diagnostics, representative cases from test distributions, and classical mutual information from secure key rates. The paired confidence interval does not support or claim optimized superiority over analytic correction.
- Report-only mode preserves simulation provenance in `manifest.json` and records rendering provenance separately. HTML text is escaped; YAML and NPZ loading use safe/non-pickle paths.
- Setup is confined to documented local virtual environments; dependency synchronization and replacement of named run outputs are disclosed. No push or remote repository operation was performed.

## Nonblocking follow-ups

1. **Input validation is incomplete for arbitrary custom configurations.** `config.merge_config` does not uniformly reject nonfinite waist, pupil radius, learning rate, or distortion means, and unknown distortion keys can be silently ineffective. Tighten finite/type/key checks and add negative tests before treating this as a general-purpose configuration API. The checked baseline is finite and valid; this does not invalidate its results.
2. **Exact source provenance is not frozen.** The saved manifest honestly records a dirty Git tree, and this project currently appears untracked in the enclosing repository. A revision plus dirty flag cannot recover the exact implementation. Before distribution/publication, archive source hashes or an immutable local source snapshot; dependency freezes also lack wheel hashes. No clean-host reinstall was attempted here.
3. **Output replacement is not transactional.** Interrupted runs can leave mixed-generation artifacts in a reused output directory; stale unrelated files can be included in the inventory. The README already recommends a fresh directory per configuration. Atomic staging/finalization and an explicit completion marker would make this more robust.
4. **Off-baseline conditioning differs intentionally between data and figure.** Archived conditional samples use rotated Alice, whereas Figure 7 selects original Alice X. Labels and limitations acknowledge the distinction and the selections coincide under baseline phase compensation. A common explicit selector would simplify future maintenance.
5. **Coverage is strongest at the numerical/core layer.** Add CLI/report-only provenance, malformed-configuration, and interrupted-output regression tests. Internal TorchOptics FFT imports are pinned but fragile across upgrades. The compressed one-line style in several modules also makes future review harder.

## Limits and modifications

The full optimization/rendering pipeline and clean environment installation were not rerun during this bounded review; existing artifact integrity and numerical consistency were independently checked instead. The 14 warnings are Matplotlib/Pyparsing deprecations, not test failures. Physical discretization convergence remains an expressly documented limitation rather than a newly discovered code blocker.

Only `docs/CODE_REVIEW.md` was created/modified by this review. No numerical source, configuration, dependencies, saved results, or Git history were changed.
