import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT.parent/'Front_Mission_WSC_v0.34_TEST_Publicidad_Auditoria.zip'
audit=json.loads((ROOT/'qa/audit_summary.json').read_text());runtime=json.loads((ROOT/'qa/runtime_validation.json').read_text())
assert audit['rom_sha256']==runtime['rom_sha256'] and runtime['sakata_rom_decode_equals_captured_vram']
assert all(p['roundtrip']=='PASS' for p in audit['patches'])
files=[]
for p in ROOT.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
 if p==ROOT/'SHA256SUMS_RELEASE.txt' or p==ROOT/'qa/ads_after/sakata_vram.bin':continue
 if p.suffix.lower() in {'.rom','.ws','.wsc','.sav','.srm'}:raise ValueError('Unexpected ROM/save in package')
 if p.suffix.lower()=='.bin' and p.name!='bank76.bin':raise ValueError('Unreviewed binary')
 files.append(p)
files.sort();m=ROOT/'SHA256SUMS_RELEASE.txt'
m.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files))
files=sorted(files+[m]);assert not out.exists()
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:
  info=zipfile.ZipInfo('Front_Mission_WSC_v034_TEST/'+p.relative_to(ROOT).as_posix(),(2026,9,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
  z.writestr(info,p.read_bytes())
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps(dict(path=str(out),size=out.stat().st_size,files=len(files),sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2))
