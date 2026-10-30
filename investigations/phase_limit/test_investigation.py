"""Tests written before the new investigation implementation."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[2]

def core():
    p=Path(__file__).with_name('core.py')
    assert p.exists(), 'Investigation physics implementation is not present yet'
    spec=importlib.util.spec_from_file_location('phase_core',p)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def test_nominal_two_plane_corrects_and_conserves_power():
    c=core(); g,lo,pupil,mu=c.setup(n=256) # Larger window for continuum identity
    fields=c.fields([mu],g)
    inp,phi=c.two_plane_masks(g,mu)
    result=c.evaluate(fields,lo,pupil,phi,inp)
    assert result['q'][0]>1-1e-10
    assert abs(result['power'][0]-1)<1e-10

def test_spectral_ceiling_is_attained_and_matches_continuum():
    c=core();g,lo,pupil,mu=c.setup(n=256);u=c.fields([mu],g)
    b=c.bounds(u,lo,pupil)
    phi=c.analytic(u[0],lo)
    r=c.evaluate(u,lo,pupil,phi)
    assert abs(r['eta'][0]-b['eta'][0])<1e-12
    assert abs(r['eta'][0]-c.gaussian_bound(mu))<1e-8

def test_direct_relay_and_spectral_metrics_agree():
    c=core();g,lo,pupil,mu=c.setup(n=256);u=c.fields([mu],g)
    inp,phi=c.two_plane_masks(g,mu)
    r=c.evaluate(u,lo,pupil,phi,inp)
    out=c.ift(c.ft(u*np.exp(1j*inp))*pupil*np.exp(1j*phi))
    q=abs((out*lo.conj()).sum(axis=(-2,-1)))**2
    assert np.allclose(q,r['q'],atol=1e-13)

def test_displacement_alone_preserves_fourier_magnitude():
    c=core();g,lo,pupil,mu=c.setup(n=256);p={k:0. for k in mu};p['displacement_x']=mu['displacement_x'];p['displacement_y']=mu['displacement_y']
    assert c.bounds(c.fields([p],g),lo,pupil)['eta'][0]>1-1e-10

def test_density_bound_and_passive_power():
    c=core();g,lo,pupil,mu=c.setup();pars=c.sample(16,77);u=c.fields(pars,g);lam=c.unitary_ceiling(u)
    inp,phi=c.two_plane_masks(g,mu);r=c.evaluate(u,lo,pupil,phi,inp)
    assert r['q'].mean()<=lam+1e-12
    assert 0<lam<=1+1e-12
    loss=c.evaluate(u,lo,.5*pupil,phi,inp)
    assert np.allclose(loss['q'],.25*r['q'])
    assert np.allclose(loss['eta'],r['eta'])

def test_torch_objectives_match_numpy_and_gradient():
    c=core();import torch
    g,lo,pupil,mu=c.setup();u=c.fields(c.sample(8,78),g);phi=c.analytic(u[0],lo)
    A,powr=c.coefficients(u,lo,pupil)
    z=torch.tensor(phi,dtype=torch.float64,requires_grad=True)
    tA=torch.tensor(A);tp=torch.tensor(powr)
    val=c.objective(z,tA,tp,'eta'); val.backward()
    ref=c.evaluate(u,lo,pupil,phi)['eta'].mean();assert abs(val.item()-ref)<1e-12
    idx=np.unravel_index(int(z.grad.abs().argmax()),phi.shape);h=1e-5
    plus=phi.copy();minus=phi.copy();plus[idx]+=h;minus[idx]-=h
    fd=(c.evaluate(u,lo,pupil,plus)['eta'].mean()-c.evaluate(u,lo,pupil,minus)['eta'].mean())/(2*h)
    assert abs(fd-z.grad[idx].item())<1e-8
    q=c.evaluate(u,lo,pupil,phi)['q']
    assert abs(c.objective(z,tA,tp,'power').item()-q.mean())<1e-12
    assert abs(c.objective(z,tA,tp,'information').item()-(.5*np.log2(1+c.SNR_FACTOR*q)).mean())<1e-12

def test_optimizer_includes_initial_checkpoint_and_selects_validation():
    c=core();g,lo,pupil,mu=c.setup();u=c.fields(c.sample(8,97),g);v=c.fields(c.sample(8,98),g)
    phi=c.analytic(c.fields([mu],g)[0],lo)
    out,record=c.train(u,v,lo,pupil,phi,'eta',steps=5,lr=.03)
    assert record['best_validation']>=record['initial_validation']-1e-14
    assert abs(c.evaluate(v,lo,pupil,out)['eta'].mean()-record['best_validation'])<1e-12

def test_gaussian_formula_two_plane_matches_discrete():
    c=core();g,lo,pupil,mu=c.setup();pars=c.sample(8,99);u=c.fields(pars,g)
    inp,phi=c.two_plane_masks(g,mu);r=c.evaluate(u,lo,pupil,phi,inp)
    ref=np.array([c.gaussian_two_plane(p,mu) for p in pars])
    assert np.max(abs(ref-r['q']))<1e-8
