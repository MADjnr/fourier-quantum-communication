# Fabrication roadmap — proposed, not demonstrated

## Architecture decision before fabrication

The [controlled investigation](../investigations/phase_limit/REPORT.md) finds that a better-trained single Fourier-plane mask cannot remove the dominant spectral-amplitude mismatch. First test the **two-plane analytic correction**: cancel mean tilt/defocus/astigmatism at an input or relayed image plane, then cancel mean displacement with a Fourier-plane ramp. The ideal thin-phase quadratic powers correspond to orthogonal focal lengths **46.714 mm and 140.141 mm**, plus steering phase; these are not a completed lens prescription or fabrication design.

Compare both architectures on the same measured perturbation sequence, recording coupled power and total transmission. The simulated mean break-even incremental transmission **0.473334** (3.248 dB extra loss) is only a scalar loss sensitivity result. Pixelation, diffraction efficiency, quantization, alignment, additional aberrations, finite lens apertures, and wavelength dependence need separate budgets. Benchmark any learned two-plane design against the strong analytic two-plane controller, not only against the original single-plane baseline.

## Bulk quartz CGH

The exported NumPy mask is wrapped phase in radians at a sampled bulk Fourier plane, not a production layout. Before translating it to quartz, specify wavelength-dependent material and ambient indices and measured phase-depth response. Only then use h=φ λ/[2π(nmask−nambient)] modulo one phase cycle. No material indices or dimensioned height claims are invented here.

Re-optimize using actual illuminated aperture, minimum feature size, quantization levels, lithographic bias, surface roughness, etch nonuniformity, substrate flatness, Fresnel reflection and alignment-error distribution. Determine whether simulated Fourier pixels correspond to manufacturable features; simulation grid pitch is not automatically a design rule. Quantify power lost outside the pupil and diffraction into unwanted orders. An improved normalized overlap does not compensate insertion loss.

## TFLN transmitter and mode conditioner

A 1550 nm TFLN IQ modulator can encode Gaussian coherent displacements upstream of spatial processing. A realistic proposal must include modulator transfer nonlinearity, bias drift, bandwidth, electrode impedance/loss, insertion loss, residual amplitude modulation and calibration against LO phase. This project does not model those components or imply a fabricated device exists.

A bulk 4f system is not directly an on-chip Fourier processor. Slab diffraction regions, star couplers or related integrated transformations need separate electromagnetic design, coupling/interface models, polarization control, process rules and loss budgets. An integrated phase element cannot restore photons lost upstream.

## Next three experiments

1. **Classical optical validation:** calibrate the input-plane corrector and Fourier displacement ramp, measure complex source/LO modes and independent displacement/defocus scans, and compare paired coupled power and throughput against the one-plane baseline. Use the completed analytic grid/window checks as numerical references, not a substitute for measured apparatus errors.
2. **CGH process calibration:** fabricate only a dedicated phase-depth/feature-size calibration coupon first; measure phase response and insertion loss, then re-optimize with those constraints and quantization before designing a full mask.
3. **Receiver calibration:** demonstrate shot-noise scaling versus LO power, measure electronics separately, and acquire matched one-quadrature coherent-state ensembles through known attenuation. Compare mean √T scaling and unit vacuum variance before any protocol/security claim.

None of these proposed experiments has been performed by this simulation. Fabrication readiness requires metrology, verified design rules, packaging tolerances and a measured yield/uncertainty budget. Secure CV-QKD additionally requires a separate validated security analysis.
