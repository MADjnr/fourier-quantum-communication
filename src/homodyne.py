"""One-quadrature homodyne with disjoint spawned PRNG streams, X=a+a†."""
import numpy as np

def simulate_homodyne(eta,phase,n=100000,modulation=4.,xi_rec=0.,v_el=0.,seed=1,compensate_phase=True):
    if not np.all(np.isfinite([eta,phase,modulation,xi_rec,v_el])) or not 0<=eta<=1 or min(modulation,xi_rec,v_el)<0: raise ValueError('Unphysical efficiency/noise')
    if not isinstance(n,(int,np.integer)) or n<2: raise ValueError('At least two symbols required')
    streams=[np.random.default_rng(s) for s in np.random.SeedSequence(seed).spawn(6)]
    x=streams[0].normal(0,np.sqrt(modulation),n)
    p=streams[1].normal(0,np.sqrt(modulation),n)
    theta=0. if compensate_phase else phase
    rotated=x*np.cos(theta)-p*np.sin(theta)
    signal=np.sqrt(eta)*rotated
    noise=streams[2].normal(size=n)+streams[3].normal(0,np.sqrt(xi_rec),n)+streams[4].normal(0,np.sqrt(v_el),n)
    # Independent vacuum-only calibration: never reuse residuals as calibration.
    calibration=streams[5].normal(size=n)
    y=signal+noise
    variance=float(np.var(y,ddof=1)); nv=1+xi_rec+v_el
    # Large-n normal approximation to Gaussian sample-variance CI.
    width=1.96*variance*np.sqrt(2/(n-1))
    snr=eta*modulation/nv
    m={'n_symbols':int(n),'phase_compensated':bool(compensate_phase),'lo_phase_rad':float(phase if compensate_phase else 0.),'variance_theory':float(eta*modulation+nv),'variance_empirical':variance,'variance_ci95':[max(0.,variance-width),variance+width],'noise_variance':float(np.var(noise,ddof=1)),'vacuum_calibration_variance':float(np.var(calibration,ddof=1)),'calibrated_variance_empirical':float(variance/np.var(calibration,ddof=1)),'snr_theory':float(snr),'snr_empirical':float(np.var(signal,ddof=1)/np.var(noise,ddof=1)),'mutual_information_bits':float(.5*np.log2(1+snr)),'seed':int(seed)}
    # I_AB above is for Alice's matched/rotated quadrature, not necessarily X_A.
    snr_x=eta*modulation*np.cos(theta)**2/(nv+eta*modulation*np.sin(theta)**2)
    m.update({'mutual_information_reference':'Alice rotated quadrature X_A*cos(theta)-P_A*sin(theta)', 'snr_alice_x_theory':float(snr_x),'mutual_information_alice_x_bits':float(.5*np.log2(1+snr_x))})
    # Real finite-width conditioning on Alice's matched quadrature, not a
    # model-subtracted residual masquerading as a conditional distribution.
    halfwidth=.1*np.sqrt(modulation) if modulation>0 else .1
    selected=np.abs(rotated)<=halfwidth
    edges=np.linspace(float(y.min()),float(y.max()),81)
    m.update({'snr_empirical_kind':'oracle component variance ratio; not receiver-inferred',
              'conditional_bin':{'variable':'rotated_alice','lower':-halfwidth,'upper':halfwidth,'count':int(selected.sum())},
              'scatter_kind':'Alice prepared X/P ensemble and Bob single measured quadrature; not simultaneous X/P detection'})
    return m,{'y':y,'x':x,'p':p,'rotated_alice':rotated,'residual':noise,'signal':signal,'calibration':calibration,
              'conditional_y':y[selected],'histogram_edges':edges,
              'conditional_histogram':np.histogram(y[selected],bins=edges)[0],
              'unconditional_histogram':np.histogram(y,bins=edges)[0],
              'quadrature_scatter':np.column_stack([x[:5000],p[:5000],rotated[:5000],y[:5000]])}
