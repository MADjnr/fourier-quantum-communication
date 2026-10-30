"""Controlled investigation; discrete amplitudes include sqrt(pixel area).
Original source and archives remain untouched. All propagation is scalar/ideal.
"""
from pathlib import Path
import sys
import numpy as np
import torch
from scipy.linalg import eigh

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.config import default_config
from src.propagation import Grid,fft2c as ft,ifft2c as ift
from src.modes import gaussian
from src.distortions import distorted_mode,sample_distortions
from src.masks import circular_pupil

CFG=default_config()
SNR_FACTOR=CFG['channel_transmission']*CFG['detector_efficiency']*CFG['homodyne']['modulation']/(1+CFG['homodyne']['xi_rec']+CFG['homodyne']['v_el'])

def setup(n=128,dx=12e-6):
    g=Grid(n=n,dx=dx,wavelength=CFG['grid']['wavelength'],focal_length=CFG['grid']['focal_length'])
    return g,gaussian(g,CFG['waist'])*g.dx,circular_pupil(g,CFG['pupil_radius']),dict(CFG['distortion_mean'])

def sample(n,seed,scale=1.,mean=None,std=None):
    mean=CFG['distortion_mean'] if mean is None else mean
    std=CFG['distortion_std'] if std is None else std
    return sample_distortions(n,seed,mean,{k:v*scale for k,v in std.items()})

def fields(parameters,g):
    return np.stack([distorted_mode(g,CFG['waist'],p)*g.dx for p in parameters])

def analytic(u,lo):
    return np.angle(ft(lo)*ft(u).conj())

def two_plane_masks(g,mean):
    w=CFG['waist']; k=2*np.pi/g.wavelength
    inp=-k*(mean['tilt_x']*g.X+mean['tilt_y']*g.Y)-mean['defocus']*(g.X**2+g.Y**2)/w**2-mean['astigmatism']*(g.X**2-g.Y**2)/w**2
    four=2*np.pi/(g.wavelength*g.focal_length)*(mean['displacement_x']*g.XF+mean['displacement_y']*g.YF)
    return inp,four

def coefficients(u,lo,pupil,input_phase=None):
    f=ft(u if input_phase is None else u*np.exp(1j*input_phase))*pupil
    power=np.sum(abs(f)**2,axis=(-2,-1))
    l=ft(lo); A=(f*l.conj()/np.linalg.norm(l)).reshape(len(u),-1)
    return A,power

def evaluate(u,lo,pupil,phase,input_phase=None):
    A,power=coefficients(u,lo,pupil,input_phase)
    q=abs(A@np.exp(1j*phase).ravel())**2
    return {'q':q,'power':power,'eta':np.divide(q,power,out=np.zeros_like(q),where=power>0)}

def bounds(u,lo,pupil):
    f=abs(ft(u))*abs(pupil); l=abs(ft(lo))
    power=(f*f).sum(axis=(-2,-1)); q=(f*l).sum(axis=(-2,-1))**2/(l*l).sum()
    return {'q':q,'power':power,'eta':np.divide(q,power,out=np.zeros_like(q),where=power>0)}

def gaussian_bound(p):
    w=CFG['waist'];k=2*np.pi/CFG['grid']['wavelength'];eta=1.
    for dim,sign in [('x',1),('y',-1)]:
        a=p['defocus']+sign*p['astigmatism'];bw=k*p['tilt_'+dim]*w; d=p['displacement_'+dim]/w
        eta*=2*np.sqrt(1+a*a)/(2+a*a)*np.exp(-(bw+2*a*d)**2/(2*(2+a*a)))
    return float(eta)

def gaussian_two_plane(p,mean):
    w=CFG['waist'];k=2*np.pi/CFG['grid']['wavelength'];eta=1.
    for dim,sign in [('x',1),('y',-1)]:
        a=p['defocus']+sign*p['astigmatism']-mean['defocus']-sign*mean['astigmatism']
        r=(p['displacement_'+dim]-mean['displacement_'+dim])/w
        B=k*w*(p['tilt_'+dim]-mean['tilt_'+dim])+2*a*mean['displacement_'+dim]/w
        eta*=np.exp(-r*r-(B+a*r)**2/(4+a*a))/np.sqrt(1+a*a/4)
    return float(eta)

def unitary_ceiling(u):
    v=u.reshape(len(u),-1)
    gram=v@v.conj().T/len(u)
    return float(eigh(gram,subset_by_index=[len(u)-1,len(u)-1],eigvals_only=True)[0])

def objective(phi,A,power,kind):
    q=abs(A@torch.exp(1j*phi).reshape(-1))**2
    if kind=='eta': return (q/power.clamp_min(1e-30)).mean()
    if kind=='power': return q.mean()
    if kind=='information': return (.5*torch.log2(1+SNR_FACTOR*q)).mean()
    raise ValueError(kind)

def train(u,v,lo,pupil,start,kind,steps=600,lr=.04):
    A,p=coefficients(u,lo,pupil); B,pv=coefficients(v,lo,pupil)
    A=torch.tensor(A);B=torch.tensor(B);p=torch.tensor(p);pv=torch.tensor(pv)
    phi=torch.nn.Parameter(torch.tensor(start,dtype=torch.float64));opt=torch.optim.Adam([phi],lr=lr)
    with torch.no_grad(): initial=float(objective(phi,B,pv,kind))
    best=initial;bestphi=start.copy();selected=-1;curve=[]
    for it in range(steps):
        opt.zero_grad();loss=-objective(phi,A,p,kind);loss.backward();opt.step()
        if it%5==0 or it==steps-1:
            with torch.no_grad(): tr=float(objective(phi,A,p,kind));va=float(objective(phi,B,pv,kind))
            curve.append([it,tr,va])
            if va>best:best=va;bestphi=phi.detach().numpy().copy();selected=it
    return bestphi,{'kind':kind,'steps':steps,'learning_rate':lr,'initial_validation':initial,'best_validation':best,'selected_iteration':selected,'curve':curve}
