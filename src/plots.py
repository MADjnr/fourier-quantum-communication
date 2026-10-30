"""Headless figures from saved experiment arrays; no synthesized performance data."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CASES = ['ideal', 'distorted', 'analytic', 'optimized', 'lossy']
TITLES = ['4f architecture and model boundary', 'Spatial intensity and phase',
          'Correction comparison and residual phase', 'Optimized Fourier-plane phase mask',
          'Training and held-out validation', 'Misalignment and aberration robustness',
          'Calibrated one-quadrature homodyne', 'Variance and uncertainty',
          'SNR and efficiency budget', 'Gaussian pure-loss validation']


def make_figures(arrays, metrics, directory, dpi=300):
    a, m = arrays, metrics
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.titlesize': 11, 'figure.dpi': 100,
                         'savefig.dpi': max(300, dpi), 'axes.spines.top': False,
                         'axes.spines.right': False, 'svg.fonttype': 'none'})
    records = []
    def save(fig, number):
        stem = f'{number:02d}_' + ['architecture','fields','comparison','mask','learning','robustness','homodyne','variance','snr','quantum'][number-1]
        fig.suptitle(TITLES[number-1], fontsize=15)
        for ext in ['png', 'svg']:
            fig.savefig(directory / f'{stem}.{ext}', dpi=max(300,dpi), bbox_inches='tight')
        plt.close(fig)
        records.append({'number': number, 'title': TITLES[number-1], 'stem': stem})
    def image(fig, ax, values, coord, title, phase=False, vmax=None):
        step = coord[1]-coord[0]
        extent = [(coord[0]-step/2)*1e3, (coord[-1]+step/2)*1e3]*2
        im = ax.imshow(values, origin='lower', extent=extent,
                       cmap='twilight' if phase else 'viridis',
                       vmin=-np.pi if phase else 0, vmax=np.pi if phase else vmax)
        ax.set(title=title, xlabel='x (mm)', ylabel='y (mm)')
        fig.colorbar(im, ax=ax, shrink=.75, label='Phase (rad)' if phase else 'Intensity (m⁻²)')
    fig, ax = plt.subplots(figsize=(13,5), layout='constrained'); ax.set_axis_off()
    labels = ['Gaussian IQ\nsource', 'Lens 1\nFourier map', 'Pupil + phase\nexp(iφ)', 'Lens 2\ninverse map', 'Mode projection\nonto LO']
    for j, text in enumerate(labels):
        x=.09+j*.2
        ax.text(x,.65,text,ha='center',va='center',transform=ax.transAxes,
                bbox={'boxstyle':'round,pad=.5','fc':'#e3f1f4','ec':'#266779'})
        if j<4: ax.annotate('',xy=(x+.135,.65),xytext=(x+.07,.65),xycoords='axes fraction',arrowprops={'arrowstyle':'->'})
    ax.text(.5,.36,'CLASSICAL FIELD MODEL  →  ηtotal and arg(c)  →  GAUSSIAN HOMODYNE MODEL',ha='center',transform=ax.transAxes)
    ax.text(.5,.15,f'LO branch → selected quadrature Y; independent vacuum calibration\nλ = {m["sampling"]["wavelength_m"]*1e9:g} nm; f = {m["sampling"]["focal_length_m"]*1e3:g} mm. Security model not included.',ha='center',transform=ax.transAxes)
    save(fig,1)
    fig, axes = plt.subplots(2,3,figsize=(13,8),layout='constrained')
    fields = [a['source'],a['fourier_source'],a['optimized_output']]
    vmax=max(float(np.max(abs(v)**2)) for v in fields)
    for j,(v,name,coord) in enumerate(zip(fields,['Source','Fourier plane (before mask)','Optimized detector'],[a['x_m'],a['xF_m'],a['x_m']])):
        image(fig,axes[0,j],abs(v)**2,coord,name,vmax=vmax)
        phase=np.ma.masked_where(abs(v)**2 < np.max(abs(v)**2)*1e-6,np.angle(v))
        image(fig,axes[1,j],phase,coord,name+' phase',True)
    save(fig,2)
    fig, axes = plt.subplots(2,3,figsize=(13,8),layout='constrained')
    vmax=max(float(np.max(abs(a[c+'_output'])**2)) for c in CASES[1:4])
    for j,c in enumerate(CASES[1:4]):
        v=a[c+'_output']; image(fig,axes[0,j],abs(v)**2,a['x_m'],f'{c}: ηmode={m["cases"][c]["eta_mode"]:.4f}',vmax=vmax)
        residual=np.angle(v*np.conj(a['lo'])*np.exp(-1j*m['cases'][c]['phase']))
        residual=np.ma.masked_where(abs(v*a['lo'])<np.max(abs(v*a['lo']))*1e-6,residual)
        image(fig,axes[1,j],residual,a['x_m'],'LO-relative phase (global phase removed)',True)
    save(fig,3)
    fig, axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    phase=np.angle(np.exp(1j*a['mask_optimized']))
    image(fig,axes[0],phase,a['xF_m'],'Wrapped phase',True)
    axes[1].hist(phase.ravel(),bins=50,color='#227c9d'); axes[1].set(xlabel='Wrapped phase (rad)',ylabel='Pixels',title='All grid pixels, including outside pupil')
    save(fig,4)
    fig, axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for ax,key in zip(axes,['train_curves','validation_curves']):
        curves=np.atleast_2d(a[key]); x=np.arange(curves.shape[1])
        for i,row in enumerate(curves): ax.plot(x,row,alpha=.55,label=f'Initialization {i}')
        ax.fill_between(x,curves.min(axis=0),curves.max(axis=0),alpha=.12,color='gray',label='Initialization range (not CI)')
        ax.set(xlabel='Iteration index',ylabel='Mean mode overlap',title=key.replace('_',' ')); ax.legend(fontsize=8)
    save(fig,5)
    fig,axes=plt.subplots(1,3,figsize=(14,4.5),layout='constrained')
    for ax,c in zip(axes,CASES[1:4]):
        im=ax.pcolormesh(a['robustness_displacements_m']*1e6,a['robustness_aberrations_rad'],a['robustness_'+c],shading='auto',vmin=0,vmax=1,cmap='viridis')
        ax.set(title=c,xlabel='x displacement (µm)',ylabel='Defocus coefficient (rad)')
    fig.colorbar(im,ax=axes,label='Mode overlap ηmode'); save(fig,6)
    fig,axes=plt.subplots(2,3,figsize=(13,8),layout='constrained')
    for ax,c in zip(axes.flat,CASES):
        h=m['cases'][c]['homodyne']; cal=h['vacuum_calibration_variance']
        y=a[c+'_homodyne']/np.sqrt(cal); residual=a[c+'_residual']/np.sqrt(cal)
        ax.hist(y,bins=90,density=True,alpha=.45,label='Unconditional Y')
        ax.hist(residual,bins=90,density=True,histtype='step',label='Latent noise residual')
        alice = a[c+'_alice']
        halfwidth = .1 * np.sqrt(m['config']['homodyne']['modulation'])
        selected = np.abs(alice) <= halfwidth
        if selected.sum() > 1:
            ax.hist(y[selected], bins=45, density=True, histtype='step',
                    linewidth=1.4, label=f'Y | |Alice X|≤{halfwidth:.3g} (N={selected.sum()})')
        var=h['variance_theory']/cal; nv=(1+m['config']['homodyne']['xi_rec']+m['config']['homodyne']['v_el'])/cal
        x=np.linspace(-5*np.sqrt(var),5*np.sqrt(var),400)
        for v,label,style in [(var,'Gaussian Y theory','-'),(nv,'Residual theory','--')]:
            ax.plot(x,np.exp(-x*x/(2*v))/np.sqrt(2*np.pi*v),style,label=label)
        ax.set(title=c,xlabel='Quadrature / √(measured vacuum variance)',ylabel='Density'); ax.legend(fontsize=7)
    ax = axes.flat[-1]
    alice = a['optimized_alice']; y = a['optimized_homodyne']
    cal = m['cases']['optimized']['homodyne']['vacuum_calibration_variance']
    stride = max(1, int(np.ceil(len(y)/3000)))
    ax.scatter(alice[::stride], y[::stride]/np.sqrt(cal), s=3, alpha=.2,
               rasterized=True, label=f'Every {stride}th archived symbol')
    ax.set(title='Optimized: one-quadrature ensemble (not heterodyne)',
           xlabel='Alice prepared X (nominal SNU amplitude)',
           ylabel='Bob selected Y / √(measured vacuum variance)')
    ax.legend(fontsize=7)
    save(fig,7)
    fig,ax=plt.subplots(figsize=(9,5),layout='constrained'); x=np.arange(len(CASES))
    emp=np.array([m['cases'][c]['homodyne']['variance_empirical'] for c in CASES]); ci=np.array([m['cases'][c]['homodyne']['variance_ci95'] for c in CASES])
    ax.errorbar(x,emp,yerr=np.stack([emp-ci[:,0],ci[:,1]-emp]),fmt='o',capsize=5,label='Empirical, approximate 95% CI')
    ax.scatter(x,[m['cases'][c]['homodyne']['variance_theory'] for c in CASES],marker='x',s=70,label='Theory')
    ax.axhline(1,color='gray',ls='--',label='Vacuum 1 SNU'); ax.set(xticks=x,xticklabels=CASES,ylabel='Unconditional variance (nominal SNU)'); ax.legend(); save(fig,8)
    fig,axes=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for c in CASES:
        v=m['cases'][c]; snr=v['homodyne']['snr_theory']; db=10*np.log10(max(snr,np.finfo(float).tiny))
        axes[0].scatter(v['eta_mode'],db,label=c); axes[0].annotate(c,(v['eta_mode'],db),fontsize=8,xytext=(4,4),textcoords='offset points')
    axes[0].set(xlabel='Mode overlap ηmode',ylabel='Theoretical homodyne SNR (dB)',title='Different throughput: not a single overlap law')
    for j,key in enumerate(['T_opt','eta_mode','T_channel','eta_detector','eta_total']):
        axes[1].bar(x+(j-2)*.15,[m['cases'][c][key] for c in CASES],width=.15,label=key)
    axes[1].set(xticks=x,xticklabels=CASES,ylim=(0,1.15),ylabel='Efficiency / transmission'); axes[1].legend(fontsize=8,ncol=2); save(fig,9)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for ax,key,unit in zip(axes,['mean','variance'],['Mean X','Variance (SNU)']):
        ax.plot(a['quantum_transmissivity'],a['quantum_'+key+'_theory'],label='Covariance theory')
        ax.scatter(a['quantum_transmissivity'],a['quantum_'+key+'_empirical'],marker='x',label='Monte Carlo')
        ax.set(xlabel='Pure-loss transmissivity T',ylabel=unit); ax.legend()
    save(fig,10)
    return records
