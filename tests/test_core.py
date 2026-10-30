import numpy as np
import pytest
import torch
from src.propagation import Grid, fft2c, ifft2c, propagate, torchoptics_check
from src.metrics import optical_metrics
from src.homodyne import simulate_homodyne
from src.gaussian_quantum import pure_loss


def test_fft_physical_energy_and_numpy_torch():
    g=Grid(32, 12e-6, 1550e-9, .1)
    rng=np.random.default_rng(5); u=rng.normal(size=(32,32))+1j*rng.normal(size=(32,32))
    assert np.max(abs(ifft2c(fft2c(u))-u))<1e-12
    assert np.allclose(fft2c(u),fft2c(torch.tensor(u)).numpy())
    out,F=propagate(u,np.zeros_like(u.real),g)
    assert np.allclose(out,u)
    assert np.isclose(np.sum(abs(F)**2)*g.dxf**2,np.sum(abs(u)**2)*g.dx**2)
    assert np.allclose(g.xF,g.wavelength*g.focal_length*np.fft.fftshift(np.fft.fftfreq(g.n,g.dx)))


def test_overlap_separates_power_and_phase():
    u=np.ones((8,8),complex)
    m=optical_metrics(.5j*u,u,1.,64.)
    assert m['eta_mode']==pytest.approx(1.)
    assert m['T_opt']==pytest.approx(.25)
    assert m['phase']==pytest.approx(np.pi/2)
    assert optical_metrics(u*0,u,1.,64.)['eta_mode']==0


def test_phase_gradient_matches_finite_difference():
    g=Grid(8,1e-5,1.55e-6,.1)
    torch.manual_seed(2)
    u=torch.randn(8,8,dtype=torch.complex128)
    phi=torch.randn(8,8,dtype=torch.float64,requires_grad=True)
    def f(p): return propagate(u,p,g)[0][2,3].abs().square()
    f(phi).backward(); h=1e-5
    p=phi.detach().clone(); p[1,4]+=h
    q=phi.detach().clone(); q[1,4]-=h
    assert phi.grad[1,4].item()==pytest.approx(((f(p)-f(q))/(2*h)).item(),rel=1e-5,abs=1e-8)


def test_quantum_loss():
    for t in [0,.1,.5,1]:
        mean,cov=pure_loss(np.array([2.,-1.]),np.eye(2),t)
        assert np.allclose(mean,np.sqrt(t)*np.array([2.,-1.]))
        assert np.allclose(cov,np.eye(2))


def test_noise_phase_reproducibility():
    a,arr=simulate_homodyne(.4,np.pi/2,100000,4.,0.,0.,7,False)
    b,arr2=simulate_homodyne(.4,np.pi/2,100000,4.,0.,0.,7,False)
    assert a==b and np.array_equal(arr['y'],arr2['y'])
    assert abs(a['noise_variance']-1)<.02
    assert abs(a['variance_empirical']-a['variance_theory'])<.04
    assert abs(np.corrcoef(arr['y'],arr['x'])[0,1])<.02
    assert np.corrcoef(arr['y'],arr['p'])[0,1]<-.7
    for t in [0,.1,1]:
        m,_=simulate_homodyne(t,0,100000,0,0,0,91)
        assert m['variance_ci95'][0] < 1 < m['variance_ci95'][1]


def test_torchoptics_actual_api():
    g=Grid(16,1e-5,1.55e-6,.1)
    u=np.exp(-((g.X/4e-5)**2+(g.Y/4e-5)**2)).astype(complex)
    result=torchoptics_check(u,g)
    assert result['power_error']<1e-10
    assert result['overlap_error']<1e-10
    assert result['fresnel_relative_error']<1e-7


@pytest.mark.parametrize('n',[15,16])
def test_batched_fft_roundtrip(n):
    rng=np.random.default_rng(4)
    u=rng.normal(size=(3,n,n))+1j*rng.normal(size=(3,n,n))
    assert np.allclose(ifft2c(fft2c(u)),u,atol=1e-12)
    assert np.allclose(fft2c(torch.tensor(u)).numpy(),fft2c(u),atol=1e-12)


def test_analytic_mask_and_irrecoverable_loss():
    from src.modes import gaussian
    from src.distortions import distorted_mode
    from src.masks import analytic_mask, circular_pupil
    g=Grid(32); lo=gaussian(g,8e-5)
    u=distorted_mode(g,8e-5,{'displacement_x':3e-5,'defocus':.8})
    phi=analytic_mask(u,lo)
    out,_=propagate(u,phi,g)
    assert np.allclose(abs(np.exp(1j*phi)),1)
    assert optical_metrics(out,lo,g.dx)['eta_mode']>=optical_metrics(u,lo,g.dx)['eta_mode']
    attenuated=u*(g.X>0)*np.sqrt(.08)
    out,_=propagate(attenuated,phi,g,circular_pupil(g,.002))
    assert 0<=optical_metrics(out,lo,g.dx)['T_opt']<=.08


def test_optimization_reproducible_and_selects_validation():
    from src.config import merge_config
    from src.modes import gaussian
    from src.distortions import distorted_mode
    from src.optimization import optimize_mask
    g=Grid(8); lo=gaussian(g,3e-5)
    train=np.stack([distorted_mode(g,3e-5,{'defocus':a}) for a in [.3,.7]])
    valid=np.stack([distorted_mode(g,3e-5,{'defocus':a}) for a in [.4,.8]])
    cfg=merge_config({'optimization':{'iterations':5,'initializations':2}})['optimization']
    a,ma,ta,va=optimize_mask(train,valid,lo,np.ones((8,8)),g,cfg)
    b,mb,tb,vb=optimize_mask(train,valid,lo,np.ones((8,8)),g,cfg)
    assert np.array_equal(a,b) and np.array_equal(ta,tb)
    assert ma['validation_eta']==pytest.approx(va.max())
    assert ma['validation_eta']==pytest.approx(np.mean([optical_metrics(propagate(u,a,g)[0],lo,g.dx)['eta_mode'] for u in valid]))


def test_excess_noise_snr_and_ci():
    m,a=simulate_homodyne(.3,.4,200000,4,.2,.1,21)
    assert m['variance_ci95'][0]<m['variance_theory']<m['variance_ci95'][1]
    assert m['snr_empirical']==pytest.approx(m['snr_theory'],rel=.02)
    assert abs(np.corrcoef(a['residual'],a['calibration'])[0,1])<.02
    m,_=simulate_homodyne(.3,np.pi/2,100000,4,0,0,21,False)
    assert m['mutual_information_alice_x_bits']==pytest.approx(0)


@pytest.mark.parametrize('update',[{'optimization':{'iterations':0}},{'optimization':{'test_size':1}},{'detector_efficiency':1.1},{'optimization':{'test_seed':101}}])
def test_invalid_configuration(update):
    from src.config import merge_config
    with pytest.raises(ValueError): merge_config(update)


def test_squeezed_covariance_loss_not_created_by_mask():
    _,v=pure_loss([0,0],np.diag([.5,2.]),.4)
    assert np.allclose(v,np.diag([.8,1.4]))


def test_std_only_distortion_and_validation():
    from src.distortions import sample_distortions
    values=sample_distortions(3,10,{}, {'tilt_x':.001})
    assert any(p['tilt_x']!=0 for p in values)
    assert values==sample_distortions(3,10,{}, {'tilt_x':.001})
    with pytest.raises(ValueError): sample_distortions(3,10,{}, {'tilt_x':-.001})
    with pytest.raises(ValueError): Grid(dx=float('nan'))
    with pytest.raises(ValueError): simulate_homodyne(.3,0,n=1)
    with pytest.raises(ValueError): simulate_homodyne(.3,0,xi_rec=float('nan'))
