#!/usr/bin/env python3
"""Capture reproducible checks and one bounded normal-GUI launch (never testRunner)."""
import argparse,json,subprocess,sys,hashlib,shutil,os
from pathlib import Path
from build_v032 import ROOT,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True,type=Path);p.add_argument('--mesen',required=True,type=Path);a=p.parse_args()
    ev=ROOT/'evidence';ev.mkdir(exist_ok=True)
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tools'),'-p','test_*.py','-v'],capture_output=True,text=True)
    (ev/'unit_tests.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
    if test.returncode:raise SystemExit('Unit tests failed')
    command=[str(a.mesen.resolve()),str(a.rom.resolve())]
    try:
        run=subprocess.run(command,capture_output=True,text=True,timeout=12)
        log=run.stdout+run.stderr;code=run.returncode;timed_out=False
    except subprocess.TimeoutExpired as e:
        log=(e.stdout or b'').decode(errors='replace')+(e.stderr or b'').decode(errors='replace');code=None;timed_out=True
    (ev/'mesen_normal_gui_attempt.txt').write_text(log,encoding='utf-8')
    state='BLOCKED_NO_X_SERVER' if 'XOpenDisplay failed' in log else 'LAUNCH_ATTEMPT_NOT_RUNTIME_CERTIFIED'
    result={'status':state,'rom_sha256':sha(a.rom.read_bytes()),'mesen_sha256':sha(a.mesen.read_bytes()),'command':command,'mode':'normal GUI; no --testRunner','exit_code':code,'timeout_seconds':12,'timed_out':timed_out,'display_available':bool(os.environ.get('DISPLAY')),'xvfb_available':bool(shutil.which('Xvfb')),'frames_validated':0,'runtime_screenshots':0,'visual_gameplay_certified':False}
    (ev/'runtime_result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if shutil.which('objdump'):
        cmd=['objdump','-D','-b','binary','-m','i8086','--start-address=0x781f77','--stop-address=0x78201f',str(a.rom.resolve())]
        d=subprocess.run(cmd,capture_output=True,text=True,check=True)
        (ev/'bank_boundary_reader_disassembly.txt').write_text(d.stdout,encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
