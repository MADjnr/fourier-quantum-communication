"""Public no-I/O experiment orchestration. See docs/CORE_API.md."""
import numpy as np
import torch
from .config import merge_config
from .propagation import Grid,propagate,fft2c,torchoptics_check,phase_only_bound
from .modes import gaussian
from .distortions import distorted_mode,sample_distortions
from .masks import circular_pupil,analytic_mask
from .metrics import optical_metrics
from .optimization import optimize_mask
from .homodyne import simulate_homodyne
from .gaussian_quantum import validate_quantum

def production_propagate(u,phase,grid,pupil=None):
    """TorchOptics-backed production path; NumPy propagate stays independent."""
    with torch.no_grad():
        out,F=propagate(torch.as_tensor(u,dtype=torch.complex128),phase,grid,pupil)
    return out.cpu().numpy(),F.cpu().numpy()

def paired_improvement(a,b):
    from scipy.stats import t
    d=np.asarray(a)-np.asarray(b); n=len(d)
    se=float(d.std(ddof=1)/np.sqrt(n)); mean=float(d.mean())
    width=float(t.ppf(.975,n-1)*se); ci=[mean-width,mean+width]
    return {'mean_difference':mean,'sem':se,'ci95':ci,'n':n,
            'method':'paired Student-t interval across independent test distortions',
            'improvement_demonstrated':bool(ci[0]>0),
            'conclusion':'positive improvement established' if ci[0]>0 else 'no demonstrated improvement'}

def run_experiment(config=None):
    cfg=merge_config(config); torch.set_num_threads(cfg['torch_threads'])
    g=Grid(**cfg['grid']); waist=cfg['waist']; oc=cfg['optimization']; hc=cfg['homodyne']
    lo=gaussian(g,waist); source=distorted_mode(g,waist,cfg['distortion_mean']); pupil=circular_pupil(g,cfg['pupil_radius'])
    splits={s:np.stack([distorted_mode(g,waist,p) for p in sample_distortions(oc[s+'_size'],oc[s+'_seed'],cfg['distortion_mean'],cfg['distortion_std'])]) for s in ['train','validation','test']}
    analytic=analytic_mask(source,lo)
    optimized,optmetrics,traincurves,valcurves=optimize_mask(splits['train'],splits['validation'],lo,pupil,g,oc)
    arrays={'x_m':g.x,'xF_m':g.xF,'source':source,'lo':lo,'fourier_source':fft2c(source)*g.dx/g.dxf,'mask_analytic':analytic,'mask_optimized':optimized,'train_curves':traincurves,'validation_curves':valcurves,'pupil':pupil}
    masks={'ideal':np.zeros_like(analytic),'distorted':np.zeros_like(analytic),'analytic':analytic,'optimized':optimized,'lossy':optimized}
    metrics={'config':cfg,'cases':{},'optimization':optmetrics,'torchoptics_validation':torchoptics_check(source,g),'security_statement':'Secret key rate not calculated','sampling':{'dx_m':g.dx,'dxF_m':g.dxf,'wavelength_m':g.wavelength,'focal_length_m':g.focal_length,'grid_n':g.n,'fourier_mapping':'x_F=lambda*f*f_x','maximum_represented_paraxial_angle_rad':float(np.max(abs(g.xF))/g.focal_length),'fourier_field_power_factor':g.dx/g.dxf}}
    for i,(name,mask) in enumerate(masks.items()):
        u=lo if name=='ideal' else source
        # Opaque half-plane plus neutral attenuator: genuine irreversible amplitude loss.
        if name=='lossy': u=u*(g.X>0)*np.sqrt(cfg['lossy_transmission'])
        out,F=production_propagate(u,mask,g,pupil)
        m=optical_metrics(out,lo,g.dx,1.)
        m['eta_total']=cfg['channel_transmission']*cfg['detector_efficiency']*m['T_opt']*m['eta_mode']
        m['T_channel']=cfg['channel_transmission']; m['eta_detector']=cfg['detector_efficiency']
        hm,ha=simulate_homodyne(m['eta_total'],m['phase'],hc['n_symbols'],hc['modulation'],hc['xi_rec'],hc['v_el'],hc['seed']+i,hc['compensate_phase'])
        m['homodyne']=hm; metrics['cases'][name]=m
        arrays.update({name+'_output':out,name+'_fourier':F,name+'_homodyne':ha['y'],name+'_alice':ha['x'],name+'_residual':ha['residual']})
        arrays.update({name+'_'+key:value for key,value in ha.items() if key not in ['y','x','residual']})
    metrics['test_distribution']={}
    for name in ['distorted','analytic','optimized']:
        vals=[optical_metrics(production_propagate(u,masks[name],g,pupil)[0],lo,g.dx) for u in splits['test']]
        eta=np.array([v['eta_mode'] for v in vals]); power=np.array([v['T_opt'] for v in vals])
        metrics['test_distribution'][name]={'eta_mode_mean':float(eta.mean()),'eta_mode_std':float(eta.std(ddof=1)),'eta_mode_sem':float(eta.std(ddof=1)/np.sqrt(len(eta))),'T_opt_mean':float(power.mean()),'n':len(eta),'seed':oc['test_seed']}
        arrays['test_eta_'+name]=eta
    metrics['paired_test_improvements']={a+'_minus_'+b:paired_improvement(arrays['test_eta_'+a],arrays['test_eta_'+b]) for a,b in [('optimized','analytic'),('optimized','distorted'),('analytic','distorted')]}
    displacements=np.linspace(-.00016,.00022,13); aberrations=np.linspace(0,2.8,11)
    arrays['robustness_displacements_m']=displacements; arrays['robustness_aberrations_rad']=aberrations
    for name in ['distorted','analytic','optimized']:
        heat=np.zeros((len(aberrations),len(displacements)))
        for j,a in enumerate(aberrations):
            for k,d in enumerate(displacements):
                p=dict(cfg['distortion_mean'],displacement_x=float(d),defocus=float(a))
                out,_=production_propagate(distorted_mode(g,waist,p),masks[name],g,pupil)
                heat[j,k]=optical_metrics(out,lo,g.dx)['eta_mode']
        arrays['robustness_'+name]=heat
    qm,qa=validate_quantum(seed=hc['seed']+1000,n=hc['n_symbols']); metrics['quantum_validation']=qm; arrays.update(qa)
    metrics['lossy_failure']={'description':'Half-plane occlusion and neutral attenuation before Fourier mask; input-power reference remains pre-loss unity','power_upper_bound':cfg['lossy_transmission'],'observed_throughput':metrics['cases']['lossy']['T_opt'],'cannot_recover_lost_photons':True}
    metrics['lossy_failure'].update(phase_only_bound(source*(g.X>0)*np.sqrt(cfg['lossy_transmission']),lo,g,pupil))
    return {'metrics':metrics,'arrays':arrays}
