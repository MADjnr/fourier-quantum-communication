"""Run the declared numerical protocol. Usage: .venv/bin/python investigations/phase_limit/run_study.py"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
import json,time,hashlib,subprocess,itertools,platform
from pathlib import Path
import importlib.metadata
import numpy as np
import torch
from scipy.stats import t
import core as c

HERE=Path(__file__).resolve().parent
OUT=HERE/'output';OUT.mkdir(exist_ok=True)
torch.set_num_threads(2)
start=time.time()
g,lo,pupil,mu=c.setup()
archive=np.load(c.ROOT/'results/arrays/data.npz')
original=json.loads((c.ROOT/'results/metrics.json').read_text())
nominal=c.fields([mu],g)
analytic=c.analytic(nominal[0],lo)
inp,two=c.two_plane_masks(g,mu)
masks={'analytic':analytic,'archived_optimized':archive['mask_optimized'],'uncorrected':np.zeros_like(analytic),'two_plane':two}
input_masks={'two_plane':inp}
records={}

# Selection is exclusively validation based; this completes before fresh testing.
for label,n,ts,vs,steps in [('long_original12',12,101,202,600),('expanded128',128,1101,1202,800)]:
    train=c.fields(c.sample(n,ts),g);valid=c.fields(c.sample(n,vs),g)
    best=-np.inf
    for j,initial in enumerate([np.zeros_like(analytic),np.random.default_rng(4404).normal(0,.2,analytic.shape),analytic]):
        print('TRAIN',label,j,flush=True)
        phi,rec=c.train(train,valid,lo,pupil,initial,'eta',steps=steps)
        rec.update({'n_train':n,'n_validation':n,'train_seed':ts,'validation_seed':vs,'initialization':['zero','random4404','analytic'][j]})
        records[label+f'_{j}']=rec
        if rec['best_validation']>best:best=rec['best_validation'];masks[label]=phi
    if label=='expanded128':
        for kind in ['power','information']:
            print('TRAIN',kind,flush=True)
            masks[kind],records[kind]=c.train(train,valid,lo,pupil,analytic,kind,steps=800)
            records[kind].update({'n_train':n,'n_validation':n,'train_seed':ts,'validation_seed':vs,'initialization':'analytic'})
        estimated={k:float(np.mean([p[k] for p in c.sample(n,ts)])) for k in mu}
        input_masks['two_plane_estimated'],masks['two_plane_estimated']=c.two_plane_masks(g,estimated)
np.savez_compressed(OUT/'masks.npz',**masks,**{'input_'+k:v for k,v in input_masks.items()})
(OUT/'optimization.json').write_text(json.dumps(records,indent=2))

def summary(x):
    x=np.asarray(x);n=len(x);mean=float(x.mean());se=float(x.std(ddof=1)/np.sqrt(n)) if n>1 else 0.
    half=float(t.ppf(.975,n-1)*se) if n>1 else 0.
    return {'n':n,'mean':mean,'std':float(x.std(ddof=1)) if n>1 else 0.,'ci95':[mean-half,mean+half],'min':float(x.min()),'max':float(x.max())}

def eval_set(pars):
    u=c.fields(pars,g);r={}
    for name,mask in masks.items():r[name]=c.evaluate(u,lo,pupil,mask,input_masks.get(name))
    r['adaptive_one_plane_oracle']=c.bounds(u,lo,pupil)
    return r

print('HISTORICAL REPRODUCTION',flush=True)
hist=eval_set(c.sample(24,303));histstats={k:{m:summary(v) for m,v in val.items()} for k,val in hist.items()}
repro={k:float(np.max(abs(hist[k]['eta']-archive['test_eta_'+k]))) for k in ['analytic','archived_optimized'] if 'test_eta_'+k in archive}
repro['optimized']=float(np.max(abs(hist['archived_optimized']['eta']-archive['test_eta_optimized'])))
assert max(repro.values())<1e-12
print('FRESH TEST',flush=True)
allr={};allpars=[];seedid=[];seedstats=[];seedbounds=[]
for seed in [1303,2303,3303,4303,5303]:
    print('TEST seed',seed,flush=True)
    pars=c.sample(256,seed);r=eval_set(pars);allpars.extend(pars);seedid.extend([seed]*len(pars))
    seedstats.append({'seed':seed,**{k:float(v['q'].mean()) for k,v in r.items()}})
    for k,val in r.items():
        for met,a in val.items():allr.setdefault(k+'__'+met,[]).append(a)
    seedbounds.append({'seed':seed,'unitary_ceiling':c.unitary_ceiling(c.fields(pars,g))})
allr={k:np.concatenate(v) for k,v in allr.items()}
stats={k:{m:summary(allr[k+'__'+m]) for m in ['eta','q','power']} for k in r}
paired={k:summary(allr[k+'__q']-allr['analytic__q']) for k in r if k!='analytic'}
paired['two_plane_at_90pct_transmission']=summary(.9*allr['two_plane__q']-allr['analytic__q'])
paired['two_plane_at_50pct_transmission']=summary(.5*allr['two_plane__q']-allr['analytic__q'])
np.savez_compressed(OUT/'scores.npz',**allr,seed=np.array(seedid),parameters=np.array([[p[k] for k in mu] for p in allpars]),parameter_names=np.array(list(mu)),**{'historical_'+k+'__'+m:v for k,r in hist.items() for m,v in r.items()})

print('FACTORIAL ABLATION',flush=True)
factorial=[]
groups={'displacement':['displacement_x','displacement_y'],'tilt':['tilt_x','tilt_y'],'defocus':['defocus'],'astigmatism':['astigmatism']}
for bits in itertools.product([0,1],repeat=4):
    active=[k for k,b in zip(groups,bits) if b];keys=[v for k in active for v in groups[k]]
    mean={k:(v if k in keys else 0.) for k,v in mu.items()};std={k:(v if k in keys else 0.) for k,v in c.CFG['distortion_std'].items()}
    u0=c.fields([mean],g);phi=c.analytic(u0[0],lo);a,b=c.two_plane_masks(g,mean)
    pars=c.sample(256,6303,mean=mean,std=std);u=c.fields(pars,g)
    factorial.append({'active':active,'nominal_ceiling':float(c.bounds(u0,lo,pupil)['eta'][0]),'continuum_ceiling':c.gaussian_bound(mean),'single_fixed':float(c.evaluate(u,lo,pupil,phi)['q'].mean()),'single_adaptive_bound':float(c.bounds(u,lo,pupil)['q'].mean()),'two_fixed':float(c.evaluate(u,lo,pupil,b,a)['q'].mean())})

print('JITTER SWEEP',flush=True)
jitter=[]
for scale in [0,.5,1,2,4]:
    pars=c.sample(256,7303,scale);u=c.fields(pars,g)
    one=c.evaluate(u,lo,pupil,analytic);twores=c.evaluate(u,lo,pupil,two,inp)
    jitter.append({'scale':scale,'single':float(one['q'].mean()),'two':float(twores['q'].mean()),'oracle':float(c.bounds(u,lo,pupil)['q'].mean()),'unitary_ceiling':c.unitary_ceiling(u),'two_continuum':float(np.mean([c.gaussian_two_plane(p,mu) for p in pars]))})

print('GRID CONVERGENCE',flush=True)
grids=[]
pars=c.sample(32,8303)
for n,dx in [(128,12e-6),(256,6e-6),(256,12e-6),(512,6e-6)]:
    gg,ll,pp,mm=c.setup(n,dx);uu=c.fields(pars,gg);nom=c.fields([mu],gg)
    aa=c.analytic(nom[0],ll);ii,ff=c.two_plane_masks(gg,mu)
    rr=c.evaluate(uu,ll,pp,ff,ii);ss=c.evaluate(uu,ll,pp,aa)
    grids.append({'n':n,'dx':dx,'window':n*dx,'single':float(ss['q'].mean()),'two':float(rr['q'].mean()),'max_two_vs_continuum':float(np.max(abs(rr['q']-np.array([c.gaussian_two_plane(p,mu) for p in pars])))),'max_bound_vs_continuum':float(np.max(abs(c.bounds(uu,ll,pp)['q']-np.array([c.gaussian_bound(p) for p in pars]))))})

print('PUPIL AND LOSS',flush=True)
pupilcheck={}
u=c.fields(c.sample(256,1303),g)
for rad in [.0003,.0006,.001,.003,.0064]:
    pp=(g.XF**2+g.YF**2<=rad**2).astype(float)
    pupilcheck[str(rad)]={}
    for name,phi,ip in [('single',analytic,None),('two',two,inp)]:
        rr=c.evaluate(u,lo,pp,phi,ip);pupilcheck[str(rad)][name]={k:float(v.mean()) for k,v in rr.items()}

nominal_results={k:{m:float(a[0]) for m,a in c.evaluate(nominal,lo,pupil,phi,input_masks.get(k)).items()} for k,phi in masks.items()}
nominal_results['oracle']={m:float(a[0]) for m,a in c.bounds(nominal,lo,pupil).items()}
# Independent continuum Monte Carlo uses independent formula, no FFT and no fitting.
big=c.sample(100000,9303)
population={'n':len(big),'seed':9303,'single_adaptive_ceiling':summary([c.gaussian_bound(p) for p in big]),'two_fixed':summary([c.gaussian_two_plane(p,mu) for p in big])}

result={'scope':'Ideal scalar FFT relay; numerical verification, not hardware validation','config':c.CFG,'parameter_estimate':estimated,'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=c.ROOT,text=True).strip(),'reproduction_max_abs_error':repro,'historical':histstats,'historical_original_paired':original['paired_test_improvements']['optimized_minus_analytic'],'fresh':stats,'paired_q_vs_analytic':paired,'seed_means':seedstats,'empirical_unitary_bounds':seedbounds,'nominal':nominal_results,'factorial':factorial,'jitter':jitter,'grids':grids,'pupil':pupilcheck,'independent_continuum_mc':population,'snr_factor':c.SNR_FACTOR,'loss_break_even':stats['analytic']['q']['mean']/stats['two_plane']['q']['mean'],'versions':{k:importlib.metadata.version(k) for k in ['numpy','scipy','torch','torchoptics','matplotlib']},'python':platform.python_version(),'runtime_seconds':time.time()-start,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'core.py',HERE/'run_study.py',HERE/'PROTOCOL.md',HERE/'test_investigation.py']}}
(OUT/'results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'fresh':{k:v['q']['mean'] for k,v in stats.items()},'primary_difference':paired['two_plane'],'runtime_seconds':time.time()-start},indent=2),flush=True)
