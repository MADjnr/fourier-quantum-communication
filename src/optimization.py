"""Train-only autograd, validation-only checkpoint selection, untouched test set."""
import time
import numpy as np
import torch
from .propagation import fft2c, modulate_fourier


def spectral_objective(phi,fields,target,pupil,grid):
    """Actual batched normalized training score, including pupil and power."""
    masked=modulate_fourier(fields,phi,grid,pupil)
    numerator=(target.conj()*masked).sum(dim=(-2,-1)).abs().square()
    denominator=target.abs().square().sum()*masked.abs().square().sum(dim=(-2,-1))
    return (numerator/denominator.clamp_min(1e-30)).mean()


def objective_gradient_check(fields,target,pupil,grid):
    generator=torch.Generator().manual_seed(793)
    phi=(.2*torch.randn((grid.n,grid.n),generator=generator,dtype=torch.float64)).requires_grad_()
    score=spectral_objective(phi,fields,target,pupil,grid)
    grad,=torch.autograd.grad(score,phi)
    # Strongest coordinate avoids a vacuous check outside a finite pupil.
    index=np.unravel_index(int(grad.abs().argmax()),tuple(phi.shape)); h=1e-5
    plus=phi.detach().clone(); minus=plus.clone(); plus[index]+=h; minus[index]-=h
    fd=float((spectral_objective(plus,fields,target,pupil,grid)-spectral_objective(minus,fields,target,pupil,grid))/(2*h))
    ad=float(grad[index]); error=abs(fd-ad); tolerance=1e-8+1e-5*abs(fd)
    return {'autograd':ad,'finite_difference':fd,'absolute_error':error,'tolerance':tolerance,'passed':error<=tolerance,'step':h,'coordinate':[int(i) for i in index],'objective':'actual batched normalized pupil overlap'}


def optimize_mask(train,validation,lo,pupil,grid,config):
    start=time.perf_counter()
    # Parseval eliminates only the redundant inverse transform; production
    # TorchOptics Field modulation and physical Fourier sampling are shared.
    spectra=fft2c(torch.tensor(train,dtype=torch.complex128))*grid.dx/grid.dxf
    valid=fft2c(torch.tensor(validation,dtype=torch.complex128))*grid.dx/grid.dxf
    target=fft2c(torch.tensor(lo,dtype=torch.complex128))*grid.dx/grid.dxf
    pupil=torch.tensor(pupil,dtype=torch.float64)
    def score(phi,fields):
        return spectral_objective(phi,fields,target,pupil,grid)
    gradient_check=objective_gradient_check(spectra,target,pupil,grid)
    trains=[]; valids=[]; summaries=[]; best=-1.; best_phi=None
    for init in range(config['initializations']):
        generator=torch.Generator().manual_seed(config['initialization_seed']+init)
        phi=torch.nn.Parameter(.2*torch.randn((grid.n,grid.n),generator=generator,dtype=torch.float64) if init else torch.zeros((grid.n,grid.n),dtype=torch.float64))
        optimizer=torch.optim.Adam([phi],lr=config['learning_rate'])
        tc=[]; vc=[]; local_best=-1.; best_iteration=0
        for iteration in range(config['iterations']):
            optimizer.zero_grad(); loss=-score(phi,spectra); loss.backward(); optimizer.step()
            with torch.no_grad():
                tr=float(score(phi,spectra)); va=float(score(phi,valid))
                tc.append(tr); vc.append(va)
                if va>local_best: local_best=va; best_iteration=iteration
                if va>best:
                    best=va; best_phi=phi.detach().numpy().copy(); selected=init; selected_iteration=iteration
        trains.append(tc); valids.append(vc)
        summaries.append({'initialization':init,'seed':config['initialization_seed']+init,'best_validation_eta':local_best,'best_iteration':best_iteration})
    return np.angle(np.exp(1j*best_phi)), {'gradient_check':gradient_check,'selected_initialization':selected,'selected_iteration':selected_iteration,'validation_eta':best,'runs':summaries,'runtime_seconds':time.perf_counter()-start,'objective':'mean normalized eta_mode across training realizations','checkpoint_selection':'validation only','seeds':{k:config[k] for k in ['train_seed','validation_seed','test_seed','initialization_seed']}},np.array(trains),np.array(valids)
