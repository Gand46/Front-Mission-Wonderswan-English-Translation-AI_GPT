"""Deterministic release ZIP: only patches, sources and evidence; no game ROM."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT.parent/'Front_Mission_WSC_v0.33_TEST_Correccion_Palabras.zip'
expected='6c722fe5f3bbe7bf6ec371bc54a4ba801806e2c829b6ac72406b30445dd5ed41'
runs=[]
for name in ('route','primary','secondary','secondary_controls','stress','stress_narrow','before_v032'):
 p=ROOT/'qa'/name/'final.json';d=json.loads(p.read_text())
 assert d['passed'] and d['process_exit']==0 and not d['timed_out'],name
 if name not in ('stress','stress_narrow','before_v032'):assert d['rom_sha256']==expected
 else:assert d['rom_sha256']!=expected
 lua=json.loads(p.with_suffix('.lua.json').read_text())
 if name=='primary':assert len(lua['cases'])==8 and all(c['captured'] and c['reads']>=2 for c in lua['cases'])
 if name in ('secondary','secondary_controls','before_v032'):assert lua['reads_983']>=2 and lua['reads_984']>=2
 runs.append(dict(name=name,rom_sha256=d['rom_sha256'],execution='PASS',evidence=f'qa/{name}',report=lua))
(ROOT/'qa/runtime_summary.json').write_text(json.dumps(dict(version='v0.33-TEST',rom_sha256=expected,runs=runs,visual_review='See QA_ES.md for individually reviewed screenshots and scope',whole_game_approved=False),indent=2)+'\n')
def included(p):
 if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':return False
 if p.name=='SHA256SUMS_RELEASE.txt':return False
 if p.suffix.lower() in ('.wsc','.ws','.rom','.sav','.srm'):raise ValueError(f'ROM/save in release: {p}')
 if p.suffix.lower()=='.bin' and p.relative_to(ROOT).as_posix()!='source/bank76.bin':raise ValueError(f'Unreviewed binary: {p}')
 return True
files=sorted(p for p in ROOT.rglob('*') if included(p))
sums=''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in files)
manifest=ROOT/'SHA256SUMS_RELEASE.txt';manifest.write_text(sums)
files=sorted(files+[manifest])
assert not OUTPUT.exists(),'Choose a new package name instead of overwriting'
with zipfile.ZipFile(OUTPUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:
  info=zipfile.ZipInfo('Front_Mission_WSC_v033_TEST/'+p.relative_to(ROOT).as_posix(),(2026,9,20,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
  z.writestr(info,p.read_bytes())
with zipfile.ZipFile(OUTPUT) as z:assert z.testzip() is None
print(json.dumps(dict(path=str(OUTPUT),files=len(files),size=OUTPUT.stat().st_size,sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()),indent=2))
