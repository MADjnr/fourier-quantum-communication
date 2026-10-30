import numpy as np
from .modes import gaussian

def distorted_mode(grid,waist,parameters):
    p=parameters
    u=gaussian(grid,waist,p.get('displacement_x',0),p.get('displacement_y',0))
    x,y=grid.X/waist,grid.Y/waist
    phi=2*np.pi/grid.wavelength*(p.get('tilt_x',0)*grid.X+p.get('tilt_y',0)*grid.Y)
    phi=phi+p.get('defocus',0)*(x*x+y*y)+p.get('astigmatism',0)*(x*x-y*y)
    return u*np.exp(1j*phi)

def sample_distortions(n,seed,mean,std):
    if n<1 or any(not np.isfinite(v) or v<0 for v in std.values()): raise ValueError('Invalid sample count/distortion standard deviation')
    rng=np.random.default_rng(seed)
    keys=list(dict.fromkeys([*mean,*std]))
    return [{k:float(mean.get(k,0)+rng.normal()*std.get(k,0)) for k in keys} for _ in range(n)]
