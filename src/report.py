"""Evidence-linked eight-part captions and dependency-free HTML reporting."""
from pathlib import Path
import html
import json
import numpy as np


def interpretations(a, m):
    c=m['cases']; cfg=m['config']; opt=m['optimization']
    efficiency='; '.join(f'{k}: ηmode={v["eta_mode"]:.5f}, Topt={v["T_opt"]:.5f}' for k,v in c.items())
    backend_note = m['quantum_validation'].get('reason', m['quantum_validation']['backend']) + ' Backend identity is archived, not inferred from the rendering environment; no quantum-security simulation is claimed.'
    rows=[
        ('Where does the classical model end?', 'Position in mm, wavelength in nm; ηtotal dimensionless.', 'Configured grid, focal length, channel and detector efficiencies.', f'Configured λ={m["sampling"]["wavelength_m"]*1e9:g} nm; grid N={m["sampling"]["grid_n"]}; optimized ηtotal={c["optimized"]["eta_total"]:.6g}.', 'A sampled Fourier transform, pupil and phase mask determine projection onto the LO; Gaussian sampling follows.', 'Failure of power/overlap tests would invalidate the optical-to-statistical interface.', 'Diagram is an operator schematic, not a finite-distance lens-by-lens experimental validation.', 'Bulk lenses expose a Fourier plane; an integrated slab/star coupler requires independent design.'),
        ('How are intensity and phase redistributed?', 'Intensity in m⁻², coordinates mm, wrapped phase rad.', 'Same source and optimized mask; Fourier coordinates use a different physical pitch.', f'Source power={np.sum(abs(a["source"])**2)*m["sampling"]["dx_m"]**2:.6g}; optimized output power={np.sum(abs(a["optimized_output"])**2)*m["sampling"]["dx_m"]**2:.6g}.', 'FFT scaling dx/dxF preserves integrated power between physical planes.', 'A mismatch between integrated powers beyond pupil loss would falsify normalization.', 'Common linear intensity scale may hide weak Fourier detail; phase below 10⁻⁶ peak intensity is masked.', 'CGH aperture and detector area must be specified in physical coordinates.'),
        ('Does phase correction improve mode matching?', 'Intensity m⁻²; LO-relative residual phase rad; overlap dimensionless.', 'Same representative distorted input, pupil and LO; correction method changes.', efficiency, 'A Fourier phase can align spectral phase but cannot match arbitrary spectral amplitudes.', 'Independent test realizations can show no improvement or worse generalization.', 'Representative maps are not population averages; global overlap phase is removed only for residual visualization.', 'Residual phase and amplitude both matter; a phase-depth calibration alone cannot guarantee coupling.'),
        ('What phase pattern was selected?', 'Fourier coordinates mm; wrapped phase rad; histogram pixel counts.', 'Validation-selected continuous phase; fixed sampling and pupil.', f'Wrapped phase range [{np.min(np.angle(np.exp(1j*a["mask_optimized"]))):.6g}, {np.max(np.angle(np.exp(1j*a["mask_optimized"]))):.6g}] rad; Fourier pitch={m["sampling"]["dxF_m"]*1e6:.6g} µm.', 'Unit-modulus modulation changes phase, not local Fourier intensity.', 'Quantization or measured phase errors can reduce held-out overlap.', 'Histogram includes unilluminated pixels; no lithographic feature or quantization constraint was optimized.', 'No dimensioned etch height is exported without material indices and process calibration.'),
        ('Does optimization generalize beyond training?', 'Iteration index; mean normalized overlap.', 'Independent train/validation seeds; multiple initialization seeds; fixed optimizer settings.', f'Selected initialization={opt["selected_initialization"]}, iteration={opt["selected_iteration"]}, validation overlap={opt["validation_eta"]:.6g}; independent optimized test mean={m["test_distribution"]["optimized"]["eta_mode_mean"]:.6g}.', 'Autograd adjusts phase using training gradients; validation chooses the checkpoint.', 'Poor independent test overlap would contradict robust generalization.', 'Initialization envelopes are ranges, not statistical confidence intervals; validation selection can overfit.', 'Training should include measured alignment and fabrication errors before manufacturing.'),
        ('How sensitive is overlap to displacement and defocus?', 'Displacement µm, defocus coefficient rad, overlap dimensionless.', 'Only displacement x and defocus are swept; other distortions fixed; no retraining.', '; '.join(f'{k}: sweep min={a["robustness_"+k].min():.5f}, max={a["robustness_"+k].max():.5f}' for k in ['distorted','analytic','optimized']), 'Displacement changes Fourier phase while aberration changes the complex spectrum.', 'A measured tolerance scan outside simulated trends would reject the distortion model.', 'Finite deterministic grid is not an uncertainty distribution or complete tolerance budget.', 'Use this scan to propose alignment tests, not to certify manufacturing tolerances.'),
        ('Do calibrated homodyne ensembles follow the Gaussian model?', 'Quadrature divided by measured vacuum standard deviation; probability density.', f'Independent noise streams; V_A={cfg["homodyne"]["modulation"]:g}, receiver noise={cfg["homodyne"]["xi_rec"]:g}, electronics={cfg["homodyne"]["v_el"]:g}.', '; '.join(f'{k}: N={v["homodyne"]["n_symbols"]}, vacuum calibration={v["homodyne"]["vacuum_calibration_variance"]:.6g}' for k,v in c.items()), 'Unconditional variance includes modulation; signal-subtracted residual contains shot, excess and electronic noise.', 'Non-Gaussian residuals or disagreement with the analytic overlay would challenge this sampler.', 'Conditional histograms select archived symbols with |Alice X| ≤ 0.1√V_A; finite-bin width and any uncompensated P rotation remain. Residual is a separate latent-noise diagnostic. Scatter pairs prepared Alice X with one Bob quadrature across symbols, not simultaneous X/P heterodyne.', 'TFLN IQ encoding and balanced homodyne require independent vacuum and electronics calibration.'),
        ('Are empirical variances consistent with predictions?', 'Nominal shot-noise units; approximate 95% sample-variance intervals.', 'Same optical efficiencies and Gaussian modulation; independent ensembles per case.', '; '.join(f'{k}: empirical−theory={v["homodyne"]["variance_empirical"]-v["homodyne"]["variance_theory"]:+.5g}, theory inside CI={v["homodyne"]["variance_ci95"][0]<=v["homodyne"]["variance_theory"]<=v["homodyne"]["variance_ci95"][1]}' for k,v in c.items()), 'Var(Y)=ηtotal V_A+1+ξrec+vel; reduced unconditional variance alone does not imply squeezing.', 'Systematic disagreement beyond sampling uncertainty would indicate a model or normalization error.', 'Normal-approximation intervals omit calibration uncertainty and multiple-comparison corrections.', 'Measure LO stability and shot-noise linearity before interpreting receiver variances.'),
        ('How do overlap and throughput jointly control SNR?', 'Linear efficiencies and homodyne SNR dB.', 'Fixed channel, detector, modulation and noise; case-dependent overlap and optical throughput.', '; '.join(f'{k}: SNR={v["homodyne"]["snr_theory"]:.6g} (linear)' for k,v in c.items()), 'ηtotal=Tchannel Topt ηmode ηdetector; the factors multiply, rather than add.', 'A passive device increasing power above its input would violate this model.', 'Zero SNR is rendered at the floating-point floor in dB; mutual information is classical and not a key rate.', 'Optimize insertion loss alongside mode matching; phase cannot restore occluded photons.'),
        ('Does coherent-state pure loss preserve vacuum variance?', 'Transmissivity dimensionless; quadrature mean and variance SNU.', 'Input mean (2, −0.8), covariance identity; independent Monte Carlo samples.', f'Backend: {m["quantum_validation"]["backend"]}; maximum mean error={m["quantum_validation"]["max_mean_error"]:.6g}; maximum variance error={m["quantum_validation"]["max_variance_error"]:.6g}.', 'μout=√T μin and Vout=T Vin+(1−T)I; a coherent state retains variance 1.', 'A reproducible T-dependent coherent variance would falsify the pure-loss implementation.', backend_note, 'Loss characterisation is required for a TFLN transmitter; a passive CGH cannot generate squeezing or entanglement.')]
    labels=['Scientific question','Variables and units','Independent / controlled variables','Observed result','Physical mechanism','Possible falsification','Limitations / artifacts','CGH / TFLN implications']
    return [list(zip(labels,row)) for row in rows]


def write_report(arrays, metrics, figures, directory):
    root=Path(directory)
    intro='Simulation only. Secret key rate not calculated. No measured or fabricated device is claimed. Phase-only correction cannot recover lost photons, squeeze vacuum, or establish quantum security.'
    md=['# Fourier-domain coherent communication report','',intro,'', '## Reproducibility','See config.json, metrics.json, manifest.json, arrays/data.npz and tables/cases.csv. Figures are generated from the archived arrays.','']
    body=['<h1>Fourier-domain coherent communication report</h1>',f'<p>{html.escape(intro)}</p>','<p>Reproducibility: config.json, metrics.json, manifest.json, arrays/data.npz, tables/cases.csv.</p>']
    conclusions = ['SNR disclosure: snr_empirical in archived metrics is Var(latent signal)/Var(latent noise), an oracle/component sampler diagnostic, not an inferred receiver SNR. CSV labels this snr_latent_component_diagnostic. Figure 9 shows theory only.']
    from scipy.stats import t
    for baseline in ['distorted', 'analytic']:
        key = 'test_eta_' + baseline
        if key not in arrays or 'test_eta_optimized' not in arrays:
            continue
        delta = np.asarray(arrays['test_eta_optimized']) - np.asarray(arrays[key])
        if delta.size < 2:
            continue
        mean = float(delta.mean()); se = float(delta.std(ddof=1)/np.sqrt(delta.size))
        half = float(t.ppf(.975, delta.size-1)*se)
        verdict = ('Positive improvement supported on this test distribution.' if mean-half > 0 else
                   'No demonstrated improvement over this baseline (95% paired interval is not wholly positive).')
        conclusions.append(f'Optimized minus {baseline}: paired mean Δηmode={mean:.8g}, SE={se:.8g}, 95% Student-t CI=[{mean-half:.8g}, {mean+half:.8g}], N={delta.size}. {verdict} Assumes independent paired test realizations; no multiple-comparison correction.')
    md.extend(['## Baseline comparison and SNR interpretation', *conclusions, ''])
    body.append('<h2>Baseline comparison and SNR interpretation</h2>' + ''.join('<p>'+html.escape(s)+'</p>' for s in conclusions))
    for fig, points in zip(figures,interpretations(arrays,metrics)):
        title=f'{fig["number"]}. {fig["title"]}'; image=f'figures/{fig["stem"]}.png'
        md.extend([f'## {title}',f'![{title}]({image})',''])
        body.extend([f'<h2>{html.escape(title)}</h2>',f'<a href="figures/{fig["stem"]}.svg"><img src="{image}" alt="{html.escape(title)}"></a>','<ol>'])
        for label,text in points:
            md.append(f'- **{label}:** {text}')
            body.append(f'<li><strong>{html.escape(label)}:</strong> {html.escape(text)}</li>')
        md.append(''); body.append('</ol>')
    for title,key in [('Independent test distribution','test_distribution'),('TorchOptics validation','torchoptics_validation'),('Gaussian backend disclosure','quantum_validation'),('Sampling','sampling')]:
        data=json.dumps(metrics[key],indent=2)
        md.extend([f'## {title}','```json',data,'```',''])
        body.append(f'<h2>{title}</h2><pre>{html.escape(data)}</pre>')
    (root/'report.md').write_text('\n'.join(md),encoding='utf-8')
    (root/'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Fourier communication report</title><style>body{max-width:1150px;margin:2em auto;padding:0 1em;font:17px/1.6 system-ui;color:#18333d}img{width:100%}li{margin:.6em 0}pre{overflow:auto;background:#eef3f5;padding:1em}</style><body>'+''.join(body)+'</body></html>',encoding='utf-8')
