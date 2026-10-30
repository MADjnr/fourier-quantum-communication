# Independent specification compliance re-review

## Verdict and scope

**PASS — required simulation baseline is defensibly satisfied under the ideal sampled focal-plane 4f convention. No remaining baseline-blocking findings.** This does not certify a finite-distance lens-by-lens model, numerical convergence for an apparatus, quantum security, fabrication readiness, or optimized superiority over analytic correction.

Reviewed against `../FOURIER_QUANTUM_COMMUNICATION_AGENT_SPEC_LINUX.md` and the previous version of this review. Inspected production optical/optimization/quantum/statistical code, plotting and reporting code, tests, physics/dependency/reference documents, setup locks, and fresh saved outputs. Independently reran:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
```

**41 passed, 14 dependency deprecation warnings, 3.09 seconds; no skips.** In particular, the actual isolated Strawberry Fields integration test executed. No source code, environments, results, or Git history were changed by this review; only this document was updated. The expensive figure pipeline was not independently rerun during this bounded review.

## Resolution of earlier findings

| Previous finding | Re-review disposition and evidence |
|---|---|
| 1. TorchOptics absent from production relay | **Resolved for the ideal focal-plane convention.** `experiment.production_propagate` takes the torch path; `propagation.modulate_fourier` uses real public `torchoptics.Field` construction and `Field.modulate` for mask/pupil at the physical Fourier pitch. The optimizer shares this modulation path. The lens transforms remain exact sampled FFT/inverse FFT operators, using FFT aliases imported from the pinned TorchOptics implementation module. Tests compare the production relay and actual normalized objective against independent NumPy detector-plane calculations. This is meaningful production integration, not a claim that an auxiliary Fresnel check validates explicit lens propagation. |
| 2. Unconditional covariance fallback | **Resolved.** An isolated `.venv-sf` executes SF Gaussian `Program`, `Coherent`, `LossChannel`, means and covariance for vacuum and displaced coherent states at 11 transmissivities. Fresh metrics identify SF 0.23.0, 22 states, maximum mean error `2.220446049250313e-16` and covariance error `0`. Actual subprocess failures are recorded before fallback; functioning-backend physics disagreement raises. NumPy, not SF measurement trajectories, generates empirical plotted homodyne samples; this is explicitly disclosed and is adequate for Gaussian homodyne moment validation. |
| 3. References and pins absent/mismatched | **Resolved at baseline level.** Official API URLs and versions are recorded in `docs/REFERENCES.md`; `requirements.txt` and `requirements-sf.txt` contain exact environment freezes; setup syncs them into separate Python 3.11.12 environments and checks imports/backend operation. Fresh main manifest versions agree with documented primary pins. Main-environment SF “not installed” is not a failure: isolated SF versions are separately recorded in quantum metrics. A clean-machine reinstall is not yet demonstrated. |
| 4. Missing conditional/scatter data | **Resolved.** All five cases archive genuine conditional Bob samples/counts, unconditional counts, Alice P, rotated Alice, signal, calibration and 5000-row scatter arrays. Figure 7 renders actual finite Alice-X-bin conditional histograms and an Alice-X/Bob-Y ensemble scatter, clearly not simultaneous heterodyne. Residual histograms remain separately labelled latent diagnostics. |
| 5. Missing analytic optical reference | **Resolved.** `test_analytic_gaussian_fourier_profile_and_width` checks continuous Gaussian-transform amplitude/profile and physical width against the production field, in addition to FFT round trip, power, mapping and NumPy comparisons. Physical window/grid convergence remains an explicitly limited, separate next step. |
| 6. Quantum validation/CI coverage | **Resolved for baseline acceptance.** Actual SF validates vacuum and coherent covariance throughout the loss grid. New parameterized tests verify pure-loss unconditional variance CIs with zero/nonzero modulation and exact chi-square residual-variance CIs at four transmissions. Figure 8 supplies principal-case variance intervals. Figure 10 still lacks per-point intervals and independently sampled vacuum curves; do not claim otherwise. |
| 7. Wrong objective gradient check | **Resolved.** The actual batched normalized pupil-overlap objective is finite-differenced and compared independently with NumPy propagation. Fresh metrics archive absolute gradient error `1.6798611113255646e-12`, tolerance `3.000846465814233e-07`, and a passing result. |
| 8. Unestablished analytic advantage | **Resolved as a reporting issue, not as a positive research result.** Report and metrics now state paired Student-t intervals and explicitly conclude no demonstrated advantage over analytic correction. See results below. |
| 9. Oracle SNR mislabeled | **Resolved.** Metrics annotate `snr_empirical_kind`, CSV uses `snr_latent_component_diagnostic`, and report/physics explicitly identify the latent-component ratio, not a receiver-inferred estimator. Figure 9 is theoretical SNR only. |
| 10. Amplitude impossibility only asserted | **Resolved.** `phase_only_bound` evaluates the tight spectral-magnitude overlap ceiling for the actual lossy input/pupil. A test shows phase alignment attains the bound and respects the power hierarchy. Fresh case-E ceiling is strictly below unity; this establishes more than failure of the reused optimized mask. |

Earlier report-only provenance issue is fixed: `--report-only` writes `render_manifest.json`, links the original simulation manifest hash, and preserves `manifest.json`. The finite-window source-renormalization convention is now explicitly documented in `PHYSICS.md`. Neither fix implies that source clipping/convergence has been experimentally validated.

## Independently checked saved evidence

The saved simulation manifest identifies the baseline command `python -m src.run --config configs/baseline.yaml`, with timestamp `2026-10-30T02:26:06.300905+00:00`. All artifact hashes listed by that manifest matched the files at inspection. Ten PNG/SVG figure pairs, Markdown/HTML reports, configurations, arrays, and case tables are present. Plotting enforces at least 300 dpi; reporting automatically supplies eight interpretation categories per figure. This review inspected generation code and artifact integrity, not a visual typography audit of every rendered image.

All five principal cases have **100,000 symbols**. Independent train/validation/test seeds are **101/202/303**, with three initialization seeds beginning at **404**; checkpoint selection uses validation, not test data. Physical throughput, normalized overlap, channel transmission and detector efficiency remain separately accounted for. Production uses one shot-noise contribution plus independent receiver/excess/electronics/calibration streams, not a new vacuum penalty per loss factor.

Recomputed paired mean differences directly from the saved NPZ agree with metrics and report:

| Held-out comparison (24 paired distortions) | Mean overlap difference | 95% paired Student-t interval | Conclusion |
|---|---:|---:|---|
| Optimized minus distorted/no mask | 0.0390005494 | [0.0358021600, 0.0421989389] | Improvement supported on this distribution |
| Optimized minus analytic | 0.0002676017 | [-0.0013716840, 0.0019068874] | **No demonstrated superiority** |

For the deliberate lossy case, pre-relay power is **0.0622056774**, post-pupil power **0.0617361971**, phase-only normalized overlap ceiling **0.2438595833**, and coupled-power ceiling **0.0150549633** relative to original input power. Lost photons cannot be recovered, and even optimally aligned spectral phase cannot remove the remaining magnitude mismatch.

The auxiliary periodic Fresnel audit reports relative error `4.1217672805341716e-16`; this is an additional API/reference check, not evidence of finite-distance lens-train validation. SF/NumPy homodyne maximum sampled mean and variance errors are respectively **0.00656945** and **0.00776008**; exact SF moment errors are separately reported above.

## Remaining nonblocking limitations / claims to avoid

1. **Architecture wording must remain qualified.** The ideal first-lens Fourier transform, physical mask/pupil modulation and inverse-image transform satisfy Stage 1's stated operator baseline. There are no explicit propagated thin lenses in production. Importing FFT aliases from TorchOptics is not itself a distinct propagation algorithm; the real package participation is `Field.modulate`. `REFERENCES.md` still says “not a complete TorchOptics relay”; read that as the lens-by-lens limitation, not as absence of production Field integration. A full finite-distance TorchOptics relay would need separate validation.
2. **Statistics are not exhaustive.** Quantum Figure 10 has no per-point confidence bars, SNR has no estimator interval, and calibration uncertainty/multiple-comparison correction are excluded. Existing principal-case variance intervals and explicit pure-loss CI tests satisfy the baseline uncertainty requirement, but do not justify claims of comprehensive statistical validation. The SF sampling plot is NumPy MC checked against separately validated Gaussian moments.
3. **Plot conditioning versus archived conditioning differs off baseline.** Arrays condition on rotated Alice; Figure 7 recomputes a bin in original Alice X. With baseline phase compensation these coincide. Without compensation the figure remains honestly labelled Alice-X conditioning, but it is not the same selection as archived `conditional_y`; avoid presenting them as identical.
4. **Physical convergence remains unproven.** Periodic FFT boundaries, sampled-window source renormalization, scalar/paraxial assumptions and absence of a window/pitch convergence study limit physical tolerance interpretations. An analytic Gaussian reference does not prove every distorted/clipped case is converged.
5. **Reproducibility is version-pinned, not independently reinstalled or wheel-hashed.** The review verified current execution and saved artifact hashes, not a clean-host installation or immutable source snapshot. Internal TorchOptics FFT imports make the version pin particularly important. The 14 warnings are dependency deprecations, not test failures.
6. **Surface the negative bound more prominently if revising the report.** The evaluated amplitude ceiling is saved in `metrics.json` and tested, but the generated narrative does not explicitly print that numerical ceiling. The machine-readable baseline deliverable is present; a dedicated failure-case annotation would improve pedagogy.

No evidence was found of claims that the mask squeezes vacuum, generates entanglement, recovers loss, establishes secure CV-QKD, or is fabrication-ready. **Secret key rate not calculated** remains explicit. Future lens-train validation, calibrated fabrication and experimental security analysis are not implied by this PASS.
