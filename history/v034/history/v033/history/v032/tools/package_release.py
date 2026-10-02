#!/usr/bin/env python3
"""Package source, evidence, patches and history. Recursively reject ROM files."""
import io,json,zipfile
from pathlib import Path
from build_v032 import ROOT,sha

FORBIDDEN={'.wsc','.ws','.rom','.sfc','.smc','.nes','.gba','.gbc','.gb','.sav','.mss'}

def inspect_zip(data,prefix=''):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        if z.testzip() is not None:raise ValueError('Corrupt archive '+prefix)
        for n in z.namelist():
            if Path(n).suffix.lower() in FORBIDDEN:raise ValueError('ROM/save in archive '+prefix+n)
            if n.endswith('.zip'):inspect_zip(z.read(n),prefix+n+'!')

def main():
    data={}
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
        if p.suffix.lower() in FORBIDDEN:raise ValueError('Unexpected ROM/save '+str(p))
        b=p.read_bytes()
        if p.suffix.lower()=='.zip':inspect_zip(b,str(p))
        data[p.relative_to(ROOT).as_posix()]=b
    data['SHA256SUMS.txt']=''.join(sha(b)+'  '+n+'\n' for n,b in sorted(data.items())).encode()
    dest=ROOT.parent/'Front_Mission_WSC_v0.32_TEST_Fuentes_Parches_QA.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(data.items()):
            info=zipfile.ZipInfo(n,(2026,9,20,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,b)
    inspect_zip(dest.read_bytes())
    with zipfile.ZipFile(dest) as z:
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            h,n=line.split('  ',1);assert sha(z.read(n))==h,n
    print(json.dumps({'path':str(dest),'size':dest.stat().st_size,'sha256':sha(dest.read_bytes()),'files':len(data),'zip_integrity':'PASS','rom_or_save_included':False},indent=2))

if __name__=='__main__':main()
