import numpy as np

def gaussian(grid,waist,dx=0.,dy=0.):
    u=np.exp(-((grid.X-dx)**2+(grid.Y-dy)**2)/waist**2).astype(complex)
    return u/np.sqrt(np.sum(abs(u)**2)*grid.dx**2)
