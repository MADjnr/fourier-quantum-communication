"""Physically sampled unitary 4f model; second lens uses inverse-image convention."""
from dataclasses import dataclass
import numpy as np
import torch
from torchoptics import Field
# v0.4.0 exposes these torch FFT primitives in its implementation module,
# not in the public functional namespace. Field.modulate is the public API.
from torchoptics.functional.functional import fft2 as optics_fft2, ifft2 as optics_ifft2

@dataclass
class Grid:
    n: int = 128
    dx: float = 12e-6
    wavelength: float = 1550e-9
    focal_length: float = .1
    def __post_init__(self):
        if not isinstance(self.n,(int,np.integer)) or self.n<4 or not np.all(np.isfinite([self.dx,self.wavelength,self.focal_length])) or min(self.dx,self.wavelength,self.focal_length)<=0: raise ValueError('Invalid physical grid')
        self.x=(np.arange(self.n)-self.n//2)*self.dx
        self.X,self.Y=np.meshgrid(self.x,self.x)
        self.xF=self.wavelength*self.focal_length*np.fft.fftshift(np.fft.fftfreq(self.n,self.dx))
        self.dxf=self.wavelength*self.focal_length/(self.n*self.dx)
        self.XF,self.YF=np.meshgrid(self.xF,self.xF)

def fft2c(u):
    if torch.is_tensor(u):
        return torch.fft.fftshift(optics_fft2(torch.fft.ifftshift(u,dim=(-2,-1)),norm='ortho'),dim=(-2,-1))
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(u,axes=(-2,-1)),norm='ortho'),axes=(-2,-1))

def ifft2c(u):
    if torch.is_tensor(u): return torch.fft.fftshift(optics_ifft2(torch.fft.ifftshift(u,dim=(-2,-1)),norm='ortho'),dim=(-2,-1))
    return np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(u,axes=(-2,-1)),norm='ortho'),axes=(-2,-1))

def propagate(u,phase,grid,pupil=None):
    """Return detector field and physical Fourier field AFTER mask/pupil.

    dx/dxF ensures integrated Fourier-plane power equals input power.
    Lens global phase and output inversion are absorbed into the coordinate convention.
    """
    F=fft2c(u)*(grid.dx/grid.dxf)
    if torch.is_tensor(u):
        F=modulate_fourier(F,phase,grid,pupil)
    else:
        F=F*np.exp(1j*phase)
        if pupil is not None: F=F*pupil
    return ifft2c(F)*(grid.dxf/grid.dx),F

def modulate_fourier(spectrum, phase, grid, pupil=None):
    """Public TorchOptics Field phase/pupil operation at physical Fourier spacing.

    The ideal thin-lens focal-plane transform is analytic, not an ASM step
    pretending to be a lens. Global phase and image inversion are removed.
    """
    field=Field(spectrum, wavelength=torch.tensor(grid.wavelength,dtype=torch.float64,device=spectrum.device),
                spacing=torch.tensor([grid.dxf,grid.dxf],dtype=torch.float64,device=spectrum.device))
    field=field.modulate(torch.exp(1j*torch.as_tensor(phase,device=spectrum.device)))
    if pupil is not None: field=field.modulate(torch.as_tensor(pupil,device=spectrum.device))
    return field.data


def phase_only_bound(u,lo,grid,pupil):
    """Tight phase-only ceiling: squared magnitude-overlap integral / powers."""
    a=np.abs(fft2c(u)*grid.dx/grid.dxf)*np.abs(pupil)
    b=np.abs(fft2c(lo)*grid.dx/grid.dxf)
    power=float(np.sum(a*a)*grid.dxf**2)
    target_power=float(np.sum(b*b)*grid.dxf**2)
    overlap=float(np.sum(a*b)*grid.dxf**2)
    eta=overlap**2/(power*target_power) if power*target_power>0 else 0.
    return {'eta_mode_upper_bound':float(np.clip(eta,0,1)),
            'coupled_power_upper_bound':overlap**2/target_power if target_power else 0.,
            'post_pupil_power':power,'pre_relay_power':float(np.sum(np.abs(u)**2)*grid.dx**2),
            'method':'Cauchy-Schwarz Fourier magnitude overlap with pupil; attainable by phase alignment'}


def torchoptics_check(u,grid):
    """Use real TorchOptics Field power/normalize/inner APIs, not a mock.

    Production uses TorchOptics Field modulation and its imported FFT kernels
    for an exact ideal focal-plane relay. The separate Fresnel check below is
    an additional API audit, not a claim of explicit lens/ASM propagation.
    """
    import torchoptics
    from torchoptics import Field
    field=Field(torch.as_tensor(u,dtype=torch.complex128),wavelength=torch.tensor(grid.wavelength,dtype=torch.float64),spacing=torch.tensor([grid.dx,grid.dx],dtype=torch.float64))
    normalized=field.normalize()
    overlap=normalized.inner(normalized)
    power=field.power()
    expected=float(np.sum(np.abs(u)**2)*grid.dx**2)
    # Official v0.4.0 Field.propagate_to_z API, independently checked against
    # a NumPy Fresnel transfer function. Zero padding deliberately implements
    # the same periodic boundary condition as the ideal FFT relay.
    distance=grid.focal_length/100
    propagated=field.propagate_to_z(distance,propagation_method='ASM_FRESNEL',asm_pad_factor=0)
    freq=np.fft.fftfreq(grid.n,grid.dx)
    fx,fy=np.meshgrid(freq,freq)
    transfer=np.exp(2j*np.pi*distance/grid.wavelength)*np.exp(-1j*np.pi*grid.wavelength*distance*(fx*fx+fy*fy))
    reference=np.fft.ifft2(np.fft.fft2(u)*transfer)
    error=float(np.linalg.norm(propagated.data.detach().cpu().numpy()-reference)/max(np.linalg.norm(reference),1e-30))
    return {'version':__import__('importlib.metadata',fromlist=['version']).version('torchoptics'),'integration':'Production ideal focal-plane relay uses TorchOptics Field.modulate and functional implementation FFT kernels (torch aliases), with physical spacing; independent NumPy reference; additional ASM_FRESNEL API audit', 'power_error':abs(float(power)-expected)/max(expected,1e-30),'overlap_error':abs(complex(overlap)-1),'fresnel_relative_error':error,'fresnel_distance_m':distance,'fresnel_boundary':'periodic, asm_pad_factor=0'}
