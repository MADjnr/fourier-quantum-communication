"""Matched exploratory controls, separate from the frozen primary run."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
import json
from pathlib import Path
import numpy as np
import torch
from scipy.stats import t
import core as c
H=Path(__file__).resolve().parent;O=H/'output';torch.set_num_threads(2)
g,lo,pupil,mu=c.setup();m=np.load(O/'masks.npz');scores=np.load(O/'scores.npz');r=json.loads((O/'results.json').read_text())
train=c.fields(c.sample(128,1101),g);val=c.fields(c.sample(128,1202),g)
newm={};records={}
for name,n,steps in [('matched12_800',12,800),('matched128_100',128,100),('matched128_800',128,800)]:
    print(name,flush=True)
    newm[name],records[name]=c.train(train[:n],val,lo,pupil,m['analytic'],'eta',steps=steps)
newm['input_screen_only']=np.zeros_like(m['analytic'])
allq={k:[] for k in newm}
for seed in [1303,2303,3303,4303,5303]:
    u=c.fields(c.sample(256,seed),g)
    for name,mask in newm.items():allq[name].extend(c.evaluate(u,lo,pupil,mask,m['input_two_plane'] if name=='input_screen_only' else None)['q'])
allq={k:np.array(v) for k,v in allq.items()}

def stats(a):
    a=np.asarray(a);v=float(a.mean());d=float(t.ppf(.975,len(a)-1)*a.std(ddof=1)/np.sqrt(len(a)))
    return {'mean':v,'ci95':[v-d,v+d],'n':len(a)}

s={k:stats(v) for k,v in allq.items()}
paired={k:stats(v-scores['analytic__q']) for k,v in allq.items()}
paired['training_size_128_minus_12']=stats(allq['matched128_800']-allq['matched12_800'])
paired['steps_800_minus_100']=stats(allq['matched128_800']-allq['matched128_100'])
paired['power_objective_minus_eta']=stats(scores['power__q']-allq['matched128_800'])
paired['information_objective_minus_eta']=stats(scores['information__q']-allq['matched128_800'])
infoq={k:scores[k+'__q'] for k in ['analytic','power','information','two_plane']};infoq['matched_eta']=allq['matched128_800']
infos={k:.5*np.log2(1+c.SNR_FACTOR*v) for k,v in infoq.items()}
info_summary={k:stats(v) for k,v in infos.items()}
info_paired={k:stats(v-infos['matched_eta']) for k,v in infos.items() if k!='matched_eta'}
# Beam-centered quadratic aberration expressed using the original global-coordinate model.
w=c.CFG['waist'];k=2*np.pi/g.wavelength
center=dict(mu)
for dim,sign in [('x',1),('y',-1)]:center['tilt_'+dim]-=2*(mu['defocus']+sign*mu['astigmatism'])*mu['displacement_'+dim]/(k*w*w)
nom=c.fields([center],g);centered=float(c.bounds(nom,lo,pupil)['q'][0])
# Known exact population means versus training-only estimated controller already frozen.
qa=scores['analytic__q'];qt=scores['two_plane__q'];qb=scores['adaptive_one_plane_oracle__q']
budget={'ratio_two_to_single':float(qt.mean()/qa.mean()),'relative_gain_percent':float((qt.mean()/qa.mean()-1)*100),'analytic_fraction_of_one_plane_bound':float(qa.mean()/qb.mean()),'fraction_of_analytic_deficit_unfixable_by_single_plane_phase':float((1-qb.mean())/(1-qa.mean())),'extra_transmission_break_even':float(qa.mean()/qt.mean()),'extra_loss_break_even_db':float(-10*np.log10(qa.mean()/qt.mean())),'two_at_90pct':float(.9*qt.mean()),'two_at_50pct':float(.5*qt.mean()),'nominal_equivalent_cylindrical_focal_m':{dim:float(np.pi*w*w/(g.wavelength*(mu['defocus']+sign*mu['astigmatism']))) for dim,sign in [('x',1),('y',-1)]}}
# Conditional information only, not secret key rate or unknown-state fading MI.
res={'matched':s,'paired_q':paired,'information_bits_per_real_quadrature_use':info_summary,'information_paired_vs_matched_eta':info_paired,'centered_quadratic_nominal_ceiling':centered,'budget':budget,'records':records}
(O/'followup.json').write_text(json.dumps(res,indent=2))
np.savez_compressed(O/'followup_masks.npz',**newm)
np.savez_compressed(O/'followup_scores.npz',**allq)
print(json.dumps({k:v for k,v in res.items() if k!='records'},indent=2),flush=True)
