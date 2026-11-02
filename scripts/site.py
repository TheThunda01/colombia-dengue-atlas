"""Run Quarto using exactly the Python interpreter selected by uv."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
command=sys.argv[1] if len(sys.argv)>1 else 'render'
if command not in {'render','preview','check'}:
    raise SystemExit('Use render, preview, or check')
quarto=shutil.which('quarto')
if not quarto:
    raise SystemExit('Quarto is not on PATH. Install Quarto 1.9.37 or add its bin directory to PATH.')
env=os.environ.copy();env['QUARTO_PYTHON']=sys.executable
env['JUPYTER_PATH']=str(Path(sys.prefix)/'share/jupyter')+os.pathsep+env.get('JUPYTER_PATH','')
args=[quarto,command]
if command!='check':args.append(str(ROOT/'site'))
if command=='preview':args+=['--host','127.0.0.1','--port','4200','--no-browser']
subprocess.run(args,cwd=ROOT,env=env,check=True)
