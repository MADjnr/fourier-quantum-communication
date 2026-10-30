# Fabrication roadmap — proposed, not demonstrated

## Bulk quartz CGH

The exported NumPy mask is wrapped phase in radians at a sampled bulk Fourier plane, not a production layout. Before translating it to quartz, specify wavelength-dependent material and ambient indices and measured phase-depth response. Only then use h=φ λ/[2π(nmask−nambient)] modulo one phase cycle. No material indices or dimensioned height claims are invented here.

Re-optimize using actual illuminated aperture, minimum feature size, quantization levels, lithographic bias, surface roughness, etch nonuniformity, substrate flatness, Fresnel reflection and alignment-error distribution. Determine whether simulated Fourier pixels correspond to manufacturable features; simulation grid pitch is not automatically a design rule. Quantify power lost outside the pupil and diffraction into unwanted orders. An improved normalized overlap does not compensate insertion loss.

## TFLN transmitter and mode conditioner

A 1550 nm TFLN IQ modulator can encode Gaussian coherent displacements upstream of spatial processing. A realistic proposal must include modulator transfer nonlinearity, bias drift, bandwidth, electrode impedance/loss, insertion loss, residual amplitude modulation and calibration against LO phase. This project does not model those components or imply a fabricated device exists.

A bulk 4f system is not directly an on-chip Fourier processor. Slab diffraction regions, star couplers or related integrated transformations need separate electromagnetic design, coupling/interface models, polarization control, process rules and loss budgets. An integrated phase element cannot restore photons lost upstream.

## Next three experiments

1. **Classical optical validation:** measure the complex source/LO modes and independent displacement/defocus scans; compare held-out overlap and throughput against predicted values and grid-convergence studies.
2. **CGH process calibration:** fabricate only a dedicated phase-depth/feature-size calibration coupon first; measure phase response and insertion loss, then re-optimize with those constraints and quantization before designing a full mask.
3. **Receiver calibration:** demonstrate shot-noise scaling versus LO power, measure electronics separately, and acquire matched one-quadrature coherent-state ensembles through known attenuation. Compare mean √T scaling and unit vacuum variance before any protocol/security claim.

None of these proposed experiments has been performed by this simulation. Fabrication readiness requires metrology, verified design rules, packaging tolerances and a measured yield/uncertainty budget. Secure CV-QKD additionally requires a separate validated security analysis.
