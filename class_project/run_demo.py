#!/usr/bin/env python3
"""Training-free ideal scalar 4f classroom demonstration (NumPy/Matplotlib only)."""
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import json
import platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


@dataclass
class Grid:
    n: int = 256
    dx: float = 12e-6
    wavelength: float = 1550e-9
    focal_length: float = .1
    waist: float = 220e-6
    displacement_x: float = 90e-6
    displacement_y: float = -35e-6
    defocus: float = 1.4

    def __post_init__(self):
        self.x = (np.arange(self.n)-self.n//2)*self.dx
        self.X, self.Y = np.meshgrid(self.x, self.x)
        self.freq = np.fft.fftshift(np.fft.fftfreq(self.n, self.dx))
        self.FX, self.FY = np.meshgrid(self.freq, self.freq)
        self.xf = self.wavelength*self.focal_length*self.freq
        self.dxf = self.wavelength*self.focal_length/(self.n*self.dx)


def ft(u):
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(u), norm='ortho'))


def ift(u):
    return np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(u), norm='ortho'))


def spectrum(u, g):
    return ft(u)*g.dx/g.dxf


def power(u, spacing):
    return float(np.sum(abs(u)**2)*spacing**2)


def overlap(u, target):
    return float(abs(np.vdot(target, u))**2/(np.vdot(u, u).real*np.vdot(target, target).real))


def phase_bound(u, target):
    a, b = abs(ft(u)), abs(ft(target))
    return float(np.sum(a*b)**2/(np.sum(a*a)*np.sum(b*b)))


def continuum(g):
    a = g.defocus
    d2 = (g.displacement_x**2+g.displacement_y**2)/g.waist**2
    return {
        'displacement_uncorrected': float(np.exp(-d2)),
        'displacement_corrected': 1.,
        'defocus_uncorrected': float(np.exp(-d2*(1+a*a/(4+a*a)))/(1+a*a/4)),
        'single_plane_bound': float(4*(1+a*a)/(2+a*a)**2*np.exp(-2*a*a*d2/(2+a*a))),
        'two_plane': 1.,
    }


def simulate(g):
    def gaussian(sx=0., sy=0.):
        u = np.exp(-((g.X-sx)**2+(g.Y-sy)**2)/g.waist**2).astype(complex)
        return u/np.sqrt(power(u, g.dx))
    target = gaussian()
    displaced = gaussian(g.displacement_x, g.displacement_y)
    quadratic = g.defocus*(g.X**2+g.Y**2)/g.waist**2
    aberrated = displaced*np.exp(1j*quadratic)
    ramp = 2*np.pi*(g.FX*g.displacement_x+g.FY*g.displacement_y)
    single_phase = np.angle(ft(target)*ft(aberrated).conj())
    return dict(target=target, displaced=displaced, aberrated=aberrated,
                shift_corrected=ift(ft(displaced)*np.exp(1j*ramp)),
                single=ift(ft(aberrated)*np.exp(1j*single_phase)),
                two=ift(ft(aberrated*np.exp(-1j*quadratic))*np.exp(1j*ramp)),
                ramp=ramp, single_phase=single_phase, upstream_phase=-quadratic)


def save_demo(out, g, r):
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.dpi': 120, 'savefig.dpi': 180})
    mapping = {'displacement_uncorrected': 'displaced', 'displacement_corrected': 'shift_corrected',
               'defocus_uncorrected': 'aberrated', 'single_plane_bound': 'single', 'two_plane': 'two'}
    numerical = {name: overlap(r[key], r['target']) for name, key in mapping.items()}
    analytic = continuum(g)
    metrics = dict(parameters=asdict(g), numerical=numerical, continuum=analytic,
                   absolute_errors={k: abs(numerical[k]-analytic[k]) for k in numerical},
                   phase_bound_direct=phase_bound(r['aberrated'], r['target']),
                   power={k: power(r[k], g.dx) for k in ['target', *mapping.values()]},
                   fourier_power={k: power(spectrum(r[k], g), g.dxf) for k in ['target', *mapping.values()]},
                   two_plane_relative_field_error=float(np.linalg.norm(r['two']-r['target'])/np.linalg.norm(r['target'])),
                   shift_relative_field_error=float(np.linalg.norm(r['shift_corrected']-r['target'])/np.linalg.norm(r['target'])),
                   environment={'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
                   model='Ideal lossless scalar 4f; inverse-image convention; no pupil, tilt or astigmatism; known fixed distortions')
    (out/'metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    np.savez_compressed(out/'fields.npz', x_m=g.x, xf_m=g.xf, **r)

    def save(fig, name):
        fig.savefig(out/(name+'.png'), bbox_inches='tight', facecolor='white')
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.set(xlim=(0, 12), ylim=(0, 4.8)); ax.axis('off')
    stages = [(0.2, 'Input plane\nDisplaced Gaussian\n+ quadratic phase'),
              (2.6, 'Upstream phase plate\nTwo-plane case only\n$-a(x^2+y^2)/w^2$'),
              (5.0, 'Lens 1\nForward transform\n$\\mathcal{F}$'),
              (7.4, 'Fourier phase plate\nSingle: phase alignment\nTwo: displacement ramp'),
              (9.8, 'Lens 2 + output\nInverse transform\n$\\mathcal{F}^{-1}$')]
    for x, label in stages:
        ax.add_patch(FancyBboxPatch((x, 2.0), 2.05, 1.45, boxstyle='round,pad=0.08', facecolor='#edf3fa', edgecolor='#255684'))
        ax.text(x+1.025, 2.72, label, ha='center', va='center', fontsize=9)
        if x<9:
            ax.annotate('', xy=(x+2.32, 2.72), xytext=(x+2.08, 2.72), arrowprops=dict(arrowstyle='->', lw=1.7))
    ax.text(6, 4.2, '01 | Two phase planes, two different jobs', ha='center', fontsize=17, weight='bold')
    ax.text(6, 1.2, 'First undo the known quadratic phase; then undo displacement with a Fourier-plane ramp.', ha='center')
    ax.text(6, .55, 'Ideal 4f relay: input — f — L1 — f — Fourier plane — f — L2 — f — output\nSchematic not to scale. Image inversion and lens global phase absorbed into coordinates.', ha='center', fontsize=10)
    save(fig, '01_optical_schematic')

    extent = [(g.x[0]-g.dx/2)*1e3, (g.x[-1]+g.dx/2)*1e3]*2
    peak = np.max(abs(r['target'])**2)
    def intensity(ax, u, title):
        im = ax.imshow(abs(u)**2/peak, extent=extent, origin='lower', cmap='magma', vmin=0, vmax=1)
        ax.set(title=title, xlabel='x (mm)', ylabel='y (mm)', xlim=(-.6,.6), ylim=(-.6,.6))
        return im
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.7), layout='constrained')
    for ax, key, title in zip(axs[:3], ['target','displaced','shift_corrected'], ['Target', 'Displaced input', 'Ramp-corrected output']):
        im = intensity(ax, r[key], title)
    fig.colorbar(im, ax=list(axs[:3]), shrink=.75, label='Intensity / target peak')
    mid = g.n//2
    for key, label, style in [('target','Target','k--'), ('displaced','Displaced','C1-'), ('shift_corrected','Corrected','C0:')]:
        axs[3].plot(g.x*1e3, abs(r[key][mid])**2/peak, style, label=label, lw=2)
    axs[3].set(xlim=(-.6,.6), xlabel='x (mm), y = 0', ylabel='Intensity / target peak', title=f"Overlap: {numerical['displacement_uncorrected']:.4f} → {numerical['displacement_corrected']:.4f}")
    axs[3].legend(fontsize=8)
    fig.suptitle('02 | Displacement only: a positive Fourier ramp restores the target', fontsize=14)
    save(fig, '02_displacement_only')

    fig, axs = plt.subplots(1, 3, figsize=(12, 3.8), layout='constrained')
    T, A, S = (spectrum(r[k], g) for k in ['target','aberrated','single'])
    amp_peak = np.max(abs(T))
    fextent = [(g.xf[0]-g.dxf/2)*1e3, (g.xf[-1]+g.dxf/2)*1e3]*2
    for ax, F, title in zip(axs[:2], [T,A], ['Target spectral amplitude', 'Displacement + defocus amplitude']):
        im = ax.imshow(abs(F)/amp_peak, extent=fextent, origin='lower', cmap='viridis', vmin=0, vmax=1)
        ax.set(title=title, xlabel='$x_F$ (mm)', ylabel='$y_F$ (mm)', xlim=(-.9,.9), ylim=(-.9,.9))
    fig.colorbar(im, ax=list(axs[:2]), shrink=.75, label='Amplitude / target spectral peak')
    for F, label, style in [(T,'Target','k--'), (A,'Before mask','C1-'), (S,'After best phase mask','C0:')]:
        axs[2].plot(g.xf*1e3, abs(F[mid])/amp_peak, style, label=label, lw=2)
    axs[2].set(xlim=(-.9,.9), xlabel='$x_F$ (mm), $y_F = 0$', ylabel='Amplitude / target spectral peak', title=f"Tight phase-only ceiling: {numerical['single_plane_bound']:.4f}")
    axs[2].legend(fontsize=8)
    fig.suptitle('03 | A Fourier phase plate cannot repair spectral amplitude mismatch', fontsize=14)
    save(fig, '03_spectral_amplitude_limit')

    fig, axs = plt.subplots(3, 4, figsize=(12, 9), layout='constrained', gridspec_kw={'height_ratios':[1,1,.65]})
    keys = ['target','aberrated','single','two']
    labels = ['Target','Uncorrected','Best single plane','Two planes']
    for j, (key, label) in enumerate(zip(keys, labels)):
        eta = overlap(r[key], r['target'])
        im = intensity(axs[0,j], r[key], f'{label}\n$\\eta$ = {eta:.6f}')
        phase = np.ma.masked_where(abs(r[key])**2 < peak*1e-4, np.angle(r[key]))
        pm = axs[1,j].imshow(phase, extent=extent, origin='lower', cmap='twilight', vmin=-np.pi, vmax=np.pi)
        axs[1,j].set(xlabel='x (mm)', ylabel='y (mm)', xlim=(-.6,.6), ylim=(-.6,.6), title='Field phase (rad)')
    fig.colorbar(im, ax=list(axs[0]), shrink=.8, label='Intensity / target peak')
    fig.colorbar(pm, ax=list(axs[1]), shrink=.8, label='Phase (rad)', ticks=[-np.pi,0,np.pi])
    grid = axs[0,0].get_gridspec()
    for ax in axs[2]: ax.remove()
    ax = fig.add_subplot(grid[2, :])
    vals = [overlap(r[k],r['target']) for k in keys[1:]]
    ax.barh(labels[1:], vals, color=['#de8840','#427bb0','#369c81'])
    ax.axvline(numerical['single_plane_bound'], color='#427bb0', linestyle='--', label='Single-plane bound')
    for j,v in enumerate(vals): ax.text(v+.012,j,f'{v:.6f}',va='center')
    ax.set(xlim=(0,1.15), xlabel='Normalized power overlap $\\eta = |\\langle u_0,u\\rangle|^2/(P_0 P)$')
    ax.legend(loc='lower right', fontsize=8)
    fig.suptitle('04 | Same aberrated input: phase alignment reaches its bound; two planes recover the field', fontsize=13)
    save(fig, '04_correction_comparison')
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent/'output')
    args = parser.parse_args()
    g = Grid()
    metrics = save_demo(args.output, g, simulate(g))
    print(json.dumps(metrics['numerical'], indent=2))
    print('Output:', args.output.resolve())


if __name__ == '__main__':
    main()
