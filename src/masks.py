import numpy as np
from .propagation import fft2c

def analytic_mask(source,target):
    """Fourier-plane phase conjugation; cannot alter spectral amplitudes."""
    return np.angle(fft2c(target)*fft2c(source).conj())

def circular_pupil(grid,radius):
    return (grid.XF**2+grid.YF**2<=radius**2).astype(float)
