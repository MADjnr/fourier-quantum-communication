# Physics and model scope

## Optical normalization and sampling

The source and LO are normalized with pixel area: sum |u|² dx² = 1. Output power relative to pre-loss input is Topt. Normalize the output only for c = sum conj(uLO) uout dx² / sqrt(PLO Pout); ηmode=|c|². The zero-power case has zero coupling. ηtotal=Tchannel Topt ηmode ηdetector; do not count clipping twice.

The centered orthonormal FFT maps fx to xF=λ f fx, with dxF=λ f/(N dx). Multiply the orthonormal spectrum by dx/dxF for a physically normalized 2D Fourier field. Image/Fourier intensities have units m⁻²; their integrals use their respective pixel areas. The inverse transform produces an image-relay convention; physical parity/global phase conventions must be matched before comparison with an apparatus.

The operator uses periodic FFT boundaries. A finite pupil clips power. Finite window size, discretization, wrap-around, high-angle content and insufficient spatial bandwidth can bias results. Inspect boundary intensities and repeat with larger window and finer pitch before treating results as converged. The manifest records array sizes and the metrics record maximum represented paraxial angle; this is a represented bandwidth, not proof that all illuminated rays are paraxial. The implementation is scalar and paraxial, excluding polarization, vector diffraction, nonlinearities, lens defects beyond prescribed aberrations, and detailed detector response.

Production propagation is an exact sampled 4f Fourier operator. TorchOptics normalization and periodic Fresnel checks are separate reference checks, not a full finite-window lens-by-lens validation. Report validation status honestly when the dependency is unavailable.

## Single-Fourier-plane phase-only limit

A Fourier phase mask exp(iφ) preserves spectral modulus. For unit-normalized spectra U,V the unconstrained maximum overlap amplitude is bounded by the integral of |U||V|; equality requires phase alignment and compatible support. Arbitrary amplitude mismatches therefore cannot be corrected exactly. A pupil or occlusion discards photons; no passive phase can restore them. Normalized overlap can improve while throughput remains low. The deliberate half-plane obstruction and attenuation uses the original pre-loss unit input as reference.

## Why a second phase plane changes the ceiling

The [new controlled investigation](../investigations/phase_limit/REPORT.md) applies this bound to the ordinary, unoccluded nominal field: analytic overlap **0.452898099** attains the ceiling. This is a restriction of **where** correction acts, not a universal limit on phase-only optics. With unit target norm, `Qmax = (integral |PU||V|)^2` and `etamax = Qmax / integral |PU|^2`; use physical integration weights. An adaptive mask that aligns phase separately for each input is a bound, not a deployable fixed mask.

For each axis, the grid-origin quadratic phase coefficient is `a = D ± A`. The continuum spectral intensity center is `q_c = k theta + 2 a d / w²`, and its variance is `(1+a²)/w²`. Defocus is the largest isolated nominal limitation, but tilt, displacement, and curvature interact; their losses are not additive. Moving the quadratic origin to the displaced beam center changes the physical model, not merely its implementation.

An input/image-plane screen with phase `-k(theta_bar_x x + theta_bar_y y) - D_bar(x²+y²)/w² - A_bar(x²-y²)/w²`, followed by a Fourier-plane ramp `2 pi (d_bar_x X_F + d_bar_y Y_F)/(lambda f)`, removes nominal distortion. The positive ramp uses this repository's forward-FFT and inverse-image convention. Both screens are fixed before evaluation. The upstream screen reshapes the spectrum before the Fourier mask; this does not violate the bound for the original spectrum. Fresh mean Q rises from **0.449020 to 0.948633**; nominal Q is essentially one.

For an ensemble of unit-power inputs, any fixed passive receiver has unconditional mean coupled power bounded by the largest eigenvalue of `rho = E[|u><u|]`. The reported empirical bounds use separate finite 256-input ensembles, not a population guarantee or confidence interval. Residual random mode diversity explains why a fixed two-plane correction does not reach unity on jittered inputs. Adaptation or multimode collection requires new receiver assumptions.

The investigation checks finer pitch and larger window on 32 shared diagnostic inputs for analytic architectures and bounds. This is stronger than an FFT round-trip check but does not establish convergence for every retrained mask or a real lens train.

## Quadratures and noise

X=a+a†, P=(a−a†)/i, [X,P]=2i (ℏ=2). Vacuum variance is 1 SNU. Coherent displacement α=(XA+iPA)/2 gives means XA,PA, independently drawn with variance VA. An uncompensated overlap phase rotates the selected Alice quadrature to XA cos θ−PA sin θ. This is single-quadrature homodyne, not simultaneous heterodyne measurement.

Y=√ηtotal Xrot + Z with Var(Z)=1+ξrec+vel; Var(Y)=ηtotal VA+1+ξrec+vel. Noise terms use disjoint PRNG streams and a separate vacuum-only calibration stream. Excess/electronic noise is receiver referred; no input-referred excess-noise interpretation is implied. Loss ports do not justify adding an independent unit vacuum contribution for each successive loss factor: coherent pure loss still has variance 1. Histograms divide both samples and analytic variances by the same measured calibration. Variance figure uses nominal SNU; its approximate Gaussian variance confidence intervals do not include calibration-estimation uncertainty.

SNR=ηtotal VA/(1+ξrec+vel). I=½log₂(1+SNR) is classical mutual information for the matched rotated quadrature. The metrics also distinguish information about the unrotated Alice X when phase compensation is off. The investigation averages this expression conditional on known realization-specific gain and phase compensation; it is not the rate of an unknown fading mixture. It is not a secret-key rate.

## Gaussian validation backend

The NumPy covariance reference implements μout=√T μin and Vout=T Vin+(1−T)I. Actual Strawberry Fields Gaussian execution in the isolated `.venv-sf` checks vacuum and displaced coherent moments using Program, Coherent and LossChannel; empirical plotted samples remain NumPy Monte Carlo. Backend identity, versions, errors and any fallback reason are recorded in quantum_validation. Only an unavailable SF subprocess triggers covariance fallback; a working backend that disagrees fails validation. Archived runs are not relabelled when software is installed. This is not arbitrary non-Gaussian or multimode quantum-security validation.

The archived snr_empirical is Var(latent signal)/Var(latent noise): an oracle-component sampler diagnostic, not an inferred receiver estimate. Figure 9 is theoretical SNR only. Figure 7 additionally selects actual Bob observations in a finite Alice-X bin (|X| ≤ 0.1√VA) and plots an Alice-X/Bob-Y ensemble scatter, not heterodyne. An uncompensated phase leaves unconditioned P contributions; a finite bin is not an exact zero-width conditional distribution.

Displaced source modes are renormalized within the sampled window. This convention does not preserve physical power lost outside that window for extreme displacement; convergence and boundary truncation must be checked before interpreting physical tolerance.

## Security boundary

Secret key rate not calculated. Security needs a vetted protocol, trusted/untrusted noise model, reconciliation efficiency and direction, parameter estimation, finite-size treatment, and Holevo-information bound. A scalar classical field plus Gaussian samples does not establish quantum security. A passive mask cannot squeeze vacuum or generate entanglement.
