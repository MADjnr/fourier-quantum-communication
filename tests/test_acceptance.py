"""Independent optical/statistical acceptance of production scientific outputs."""
import numpy as np
import pytest
import torch
from scipy.stats import chi2
from src.propagation import Grid, propagate, fft2c, phase_only_bound
from src.optimization import spectral_objective, objective_gradient_check
from src.homodyne import simulate_homodyne


def test_analytic_gaussian_fourier_profile_and_width():
    g=Grid(128,12e-6); w=100e-6
    u=np.exp(-(g.X*g.X+g.Y*g.Y)/w**2)
    _,f=propagate(torch.tensor(u),np.zeros_like(u),g)
    # Continuous transform of exp(-r²/w²), physical focal-plane amplitude.
    expected=np.pi*w*w/(g.wavelength*g.focal_length)*np.exp(
        -(np.pi*w/(g.wavelength*g.focal_length))**2*(g.XF*g.XF+g.YF*g.YF))
    assert np.linalg.norm(f.numpy()-expected)/np.linalg.norm(expected)<1e-10
    variance=(np.abs(f.numpy())**2*g.XF**2).sum()/(np.abs(f.numpy())**2).sum()
    assert variance==pytest.approx((g.wavelength*g.focal_length/(2*np.pi*w))**2,rel=1e-8)


def test_actual_optimizer_objective_gradient_and_independent_reference():
    g=Grid(16); rng=np.random.default_rng(19)
    u=rng.normal(size=(3,16,16))+1j*rng.normal(size=(3,16,16))
    lo=rng.normal(size=(16,16))+1j*rng.normal(size=(16,16))
    pupil=(g.XF**2+g.YF**2<.003**2).astype(float)
    fields=fft2c(torch.tensor(u))*g.dx/g.dxf
    target=fft2c(torch.tensor(lo))*g.dx/g.dxf
    check=objective_gradient_check(fields,target,torch.tensor(pupil),g)
    assert check['passed'] and abs(check['autograd'])>1e-8
    phi=torch.tensor(rng.normal(size=(16,16)))
    actual=float(spectral_objective(phi,fields,target,torch.tensor(pupil),g))
    from src.metrics import optical_metrics
    expected=np.mean([optical_metrics(propagate(v,phi.numpy(),g,pupil)[0],lo,g.dx)['eta_mode'] for v in u])
    assert actual==pytest.approx(expected,rel=1e-12)
    a,b=propagate(torch.tensor(u),phi,g,pupil)
    c,d=propagate(u,phi.numpy(),g,pupil)
    assert np.allclose(a.numpy(),c,atol=1e-12)
    assert np.allclose(b.numpy(),d,atol=1e-12)


@pytest.mark.parametrize('transmission',[0,.1,.5,1.])
@pytest.mark.parametrize('modulation',[0.,4.])
def test_pure_loss_variance_confidence_interval(transmission,modulation):
    m,a=simulate_homodyne(transmission,0,100000,modulation,seed=91)
    assert m['variance_ci95'][0]<1+transmission*modulation<m['variance_ci95'][1]
    # Separate coherent-state residual check with exact Gaussian chi-square CI.
    n=len(a['residual']); v=np.var(a['residual'],ddof=1)
    interval=(n-1)*v/chi2.ppf([.975,.025],n-1)
    assert interval[0]<1<interval[1]


def test_phase_only_ceiling_is_attained_and_loss_not_recovered():
    from src.modes import gaussian
    from src.masks import analytic_mask
    from src.metrics import optical_metrics
    g=Grid(64); lo=gaussian(g,100e-6)
    u=lo*(g.X>0)*np.sqrt(.08)*np.exp(1j*g.X/1e-4)
    pupil=(g.XF*g.XF+g.YF*g.YF<.001**2).astype(float)
    bound=phase_only_bound(u,lo,g,pupil)
    out,_=propagate(u,analytic_mask(u,lo),g,pupil)
    m=optical_metrics(out,lo,g.dx)
    assert m['eta_mode']==pytest.approx(bound['eta_mode_upper_bound'])
    assert bound['eta_mode_upper_bound']<1
    assert bound['coupled_power_upper_bound']<=bound['post_pupil_power']<=bound['pre_relay_power']<.08


def test_paired_interval_and_actual_conditional_arrays():
    from src.experiment import paired_improvement
    p=paired_improvement([.2,.4,.6],[.3,.4,.5])
    assert p['ci95'][0]<0<p['ci95'][1]
    assert not p['improvement_demonstrated']
    m,a=simulate_homodyne(.5,.4,10000,seed=91,compensate_phase=False)
    selected=np.abs(a['rotated_alice'])<=m['conditional_bin']['upper']
    assert np.array_equal(a['conditional_y'],a['y'][selected])
    assert a['conditional_histogram'].sum()==selected.sum()
    assert a['unconditional_histogram'].sum()==10000
    assert np.array_equal(a['quadrature_scatter'][:,3],a['y'][:5000])
