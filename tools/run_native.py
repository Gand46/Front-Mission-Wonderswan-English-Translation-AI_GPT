"""Run bounded native ending QA on canonical v035, using Mesen 2.1.1."""
import argparse, hashlib, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 'bed365a706e13338c8bebc17723fc40f3804a114520524d3ad62f180d44f42c0'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mesen',type=Path,required=True)
    ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    rom=a.rom.resolve();mesen=a.mesen.resolve();out=a.out.resolve()
    if hashlib.sha256(rom.read_bytes()).hexdigest()!=EXPECTED:
        ap.error('Expected canonical v0.35 ROM; no files modified')
    if out.exists() and any(out.iterdir()):
        ap.error('Use a new or empty output directory')
    out.mkdir(parents=True,exist_ok=True)
    lua=ROOT/'tools/validate_isolated_epilogue.lua'
    if os.name=='nt':
        env=os.environ.copy()
        env.update(MESEN_CAPTURE_PATH=str(out/'final.png'),MESEN_LUA_REPORT=str(out/'final.lua.json'))
        result=subprocess.run([str(mesen),'--testRunner','--timeout=100','--enableStdout','--doNotSaveSettings','--debug.scriptWindow.allowIoOsAccess=true',str(lua),str(rom)],env=env,timeout=110)
    else:
        wrapper=ROOT/'vendor/mesen_visualization_source_v1.1.0/scripts/mesen_visual.py'
        result=subprocess.run([sys.executable,str(wrapper),'capture','--mesen',str(mesen),'--rom',str(rom),'--lua',str(lua),'--output',str(out/'final.png'),'--timeout','100','--timeout-grace','5','--normalize-wonderswan'])
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
