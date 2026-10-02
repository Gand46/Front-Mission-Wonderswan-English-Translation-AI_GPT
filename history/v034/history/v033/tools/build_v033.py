#!/usr/bin/env python3
"""Reproducible renderer-only v0.33-TEST. Requires an owned clean/v032 ROM."""
import argparse, hashlib, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'history/v032/tools'))
from build_v032 import apply_ips, make_ips, sha, CLEAN
V32='75ddcc0c9ac17d2d188a5312c205149288e7eb6f5c4f93e795238d97f6f74185'

def build(base):
    if sha(base)==CLEAN:
        base=apply_ips(base,(ROOT/'patches/baseline_v032_from_clean.ips').read_bytes())
    if len(base)!=8388608 or sha(base)!=V32: raise ValueError('Expected clean ROM or canonical v0.32-TEST RC3')
    code=(ROOT/'source/bank76.bin').read_bytes()
    # Offsets match source/wordwrap.s linked at VMA 0; no linker relocations remain.
    assert len(code)==0xffbf
    assert base[0x76fea4:0x770000]==b'\xff'*348
    patches=[
      (0x76d17d,b'\x02',b'\x01','secondary 8-pixel advance (row A)'),
      (0x76d20d,b'\x02',b'\x01','secondary 8-pixel advance (row B)'),
      (0x76d213,bytes.fromhex('368036d63f01'),b'\xe8'+struct.pack('<H',(0xff65-0xd216)&65535)+b'\x90'*3,'secondary half-tile advance'),
      (0x76d233,base[0x76d233:0x76d2ce],code[0xd233:0xd2ce],'secondary word boundary'),
      (0x76fea4,b'\xff'*(len(code)-0xfea4),code[0xfea4:],'shared bounded word scan'),
      (0x78205f,bytes.fromhex('36803ebf09167c09'),bytes.fromhex('9a17ff0060730a90'),'primary far-call word boundary'),
    ]
    out=bytearray(base);allowed=set();report=[]
    for p,old,new,note in patches:
        assert len(old)==len(new) and base[p:p+len(old)]==old,(hex(p),'baseline mismatch')
        out[p:p+len(new)]=new;allowed.update(range(p,p+len(new)))
        report.append(dict(offset=f'0x{p:06X}',length=len(new),purpose=note,old_sha256=sha(old),new_sha256=sha(new)))
    out[-2:]=(sum(out[:-2])&65535).to_bytes(2,'little');allowed.update(range(len(out)-2,len(out)))
    changed={i for i,(a,b) in enumerate(zip(base,out)) if a!=b}
    assert changed<=allowed
    assert out[0x7427c0:0x745c38]==base[0x7427c0:0x745c38]
    return bytes(out),dict(version='v0.33-TEST',base_sha256=V32,rom_sha256=sha(out),checksum=f'{int.from_bytes(out[-2:],"little"):04X}',changed_bytes=len(changed),patches=report,text_pointer_table_unchanged=True,scope='renderer only; no text/font edits',status='static build verified; see separate runtime QA')

def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('output',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    result,report=build(a.rom.read_bytes())
    if a.output.exists():raise SystemExit('Output exists; choose a new filename')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result)
    if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
