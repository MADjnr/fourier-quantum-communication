"""Reproducible pipeline: python -m src.run --config configs/baseline.yaml."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import logging
import platform
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
import numpy as np
from .config import load_config
from .experiment import run_experiment
from .plots import make_figures
from .report import write_report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='configs/baseline.yaml')
    parser.add_argument('--output','--output-dir',default='results',help='Output directory (default: results)')
    parser.add_argument('--dpi',type=int,default=300,help='PNG resolution, minimum 300')
    parser.add_argument('--report-only',action='store_true',help='Regenerate figures/reports from saved output, without simulation')
    args=parser.parse_args(argv)
    if args.dpi<300: parser.error('--dpi must be at least 300')
    root=Path(args.output); root.mkdir(parents=True,exist_ok=True)
    for d in ['arrays','figures','tables','logs']: (root/d).mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',handlers=[logging.StreamHandler(),logging.FileHandler(root/'logs'/'run.log')])
    if args.report_only:
        metrics=json.loads((root/'metrics.json').read_text())
        with np.load(root/'arrays'/'data.npz',allow_pickle=False) as archive: arrays=dict(archive)
    else:
        config=load_config(args.config)
        logging.info('Starting CPU-compatible experiment')
        result=run_experiment(config); metrics=result['metrics']; arrays=result['arrays']
        np.savez_compressed(root/'arrays'/'data.npz',**arrays)
        np.save(root/'arrays'/'optimized_phase_rad.npy',arrays['mask_optimized'])
        (root/'metrics.json').write_text(json.dumps(metrics,indent=2,allow_nan=False)+'\n')
        (root/'config.json').write_text(json.dumps(metrics['config'],indent=2)+'\n')
    with (root/'tables'/'cases.csv').open('w',newline='') as f:
        keys=['case','eta_mode','T_opt','eta_total','phase','variance_theory','variance_empirical','snr_theory','snr_latent_component_diagnostic','mutual_information_bits']
        writer=csv.DictWriter(f,fieldnames=keys); writer.writeheader()
        for case,m in metrics['cases'].items():
            data=dict(m,**m['homodyne'],case=case)
            data['snr_latent_component_diagnostic']=data['snr_empirical']
            writer.writerow({k:data[k] for k in keys})
    logging.info('Rendering ten figure pairs')
    figures=make_figures(arrays,metrics,root/'figures',args.dpi)
    write_report(arrays,metrics,figures,root)
    versions={}
    for name in ['numpy','matplotlib','torch','torchoptics','PyYAML','strawberryfields','scipy']:
        try: versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name]='not installed'
    try:
        git=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
        dirty=bool(subprocess.run(['git','status','--porcelain'],capture_output=True,text=True,check=True).stdout)
    except (OSError,subprocess.CalledProcessError): git=None; dirty=None
    inventory={}
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name not in ['manifest.json','render_manifest.json'] and p.suffix not in ['.log']:
            inventory[str(p.relative_to(root))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    manifest={'utc':datetime.now(timezone.utc).isoformat(),'command':[sys.executable,'-m','src.run',*(sys.argv[1:] if argv is None else argv)],'python':sys.version,'platform':platform.platform(),'packages':versions,'git_revision':git,'git_dirty':dirty,'report_only':args.report_only,'figures':figures,'array_schema':{k:{'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in arrays.items()},'artifacts':inventory}
    if args.report_only:
        original = root/'manifest.json'
        manifest['simulation_manifest_sha256'] = hashlib.sha256(original.read_bytes()).hexdigest() if original.exists() else None
        manifest['provenance_note'] = 'Rendering only; simulation provenance remains in manifest.json and is not inferred from this invocation.'
    (root/('render_manifest.json' if args.report_only else 'manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    logging.info('Complete: %s',root/'report.html')

if __name__=='__main__': main()
