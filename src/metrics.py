import numpy as np

def optical_metrics(output,lo,dx,input_power=1.):
    power=float(np.sum(abs(output)**2)*dx**2)
    plo=float(np.sum(abs(lo)**2)*dx**2)
    c=complex(np.sum(lo.conj()*output)*dx**2/np.sqrt(power*plo)) if power*plo>0 else 0j
    return {'eta_mode':float(np.clip(abs(c)**2,0,1)), 'T_opt':power/input_power, 'c_real':c.real,'c_imag':c.imag,'phase':float(np.angle(c)),'power':power}
