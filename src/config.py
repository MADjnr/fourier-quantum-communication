import copy
import yaml

DEFAULT={'grid':{'n':128,'dx':12e-6,'wavelength':1550e-9,'focal_length':.1},'waist':.00022,'pupil_radius':.003,'distortion_mean':{'displacement_x':.00009,'displacement_y':-.000035,'tilt_x':.00065,'tilt_y':-.00025,'defocus':1.4,'astigmatism':.7},'distortion_std':{'displacement_x':.000018,'displacement_y':.000012,'tilt_x':.0001,'tilt_y':.00008,'defocus':.25,'astigmatism':.18},'optimization':{'iterations':100,'learning_rate':.08,'initializations':3,'train_size':12,'validation_size':12,'test_size':24,'train_seed':101,'validation_seed':202,'test_seed':303,'initialization_seed':404},'homodyne':{'n_symbols':100000,'modulation':4.,'xi_rec':.02,'v_el':.01,'seed':505,'compensate_phase':True},'channel_transmission':.8,'detector_efficiency':.9,'lossy_transmission':.08,'torch_threads':2}

def default_config(): return copy.deepcopy(DEFAULT)

def merge_config(update):
    out=default_config()
    for k,v in (update or {}).items():
        if isinstance(v,dict) and isinstance(out.get(k),dict): out[k].update(v)
        else: out[k]=v
    if out['homodyne']['n_symbols']<100000: raise ValueError('Principal cases require >=100000 symbols')
    seeds=[out['optimization'][k] for k in ['train_seed','validation_seed','test_seed']]
    if len(set(seeds))!=3: raise ValueError('Train, validation and test seeds must differ')
    oc=out['optimization']
    for k in ['iterations','initializations','train_size','validation_size','test_size']:
        if not isinstance(oc[k],int) or oc[k]<1: raise ValueError(k+' must be a positive integer')
    if oc['test_size']<2: raise ValueError('test_size must be >=2 to estimate spread')
    if not oc['learning_rate']>0: raise ValueError('learning_rate must be positive')
    for k in ['channel_transmission','detector_efficiency','lossy_transmission']:
        if not 0<=out[k]<=1: raise ValueError(k+' must be in [0,1]')
    if out['waist']<=0 or out['pupil_radius']<0: raise ValueError('Invalid waist/pupil')
    return out

def load_config(path):
    with open(path) as f: return merge_config(yaml.safe_load(f))
