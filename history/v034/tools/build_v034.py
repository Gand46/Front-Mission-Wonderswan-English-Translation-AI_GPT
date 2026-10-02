#!/usr/bin/env python3
import argparse,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'history/v033/tools'))
from build_v033 import apply_ips,make_ips,sha,CLEAN
from resources import decode,encode,descriptor
BASE='6c722fe5f3bbe7bf6ec371bc54a4ba801806e2c829b6ac72406b30445dd5ed41'

def build(source):
 if sha(source)==CLEAN:source=apply_ips(source,(ROOT/'patches/baseline_v033_from_clean.ips').read_bytes())
 if sha(source)!=BASE:raise ValueError('Expected exact clean ROM or v0.33-TEST')
 d=descriptor(source,17);start=d['start'];end=start+d['length'];raw,stop=decode(source,start)
 assert (start,end,len(raw),stop)==(0xdaea,0xeca1,6656,0xeca1)
 assert source.count(source[0x749bf6:0x749bfc])==1
 mdesc=descriptor(source,12);tilemap,_=decode(source,mdesc['start']);assert len(tilemap)==1152
 art=bytearray(raw);changed_pixels=[]
 def set_pixel(x,y,v):
  t=int.from_bytes(tilemap[(y//8)*64+(x//8)*2:(y//8)*64+(x//8)*2+2],'little')
  assert (t>>9)&15==3 and not t&0xe000
  adr=((t&511)-304)*32+(y%8)*4+(x%8)//2
  assert 0<=adr<len(art)
  shift=0 if x&1 else 4;old=(art[adr]>>shift)&15
  if old!=v:changed_pixels.append((x,y))
  art[adr]=(art[adr]&~(15<<shift))|(v<<shift)
 # Erase only the old Japanese caption's bounding rectangle.
 for y in range(123,141):
  for x in range(76,150):set_pixel(x,y,1)
 caption=json.loads((ROOT/'data/sakata_caption.json').read_text())
 for y,row in enumerate(caption['pixels']):
  for x,c in enumerate(row):set_pixel(caption['x']+x,caption['y']+y,int(c,16))
 compressed=encode(bytes(art));assert len(compressed)<=d['length'];assert decode(compressed,0)[0]==art
 out=bytearray(source);out[start:end]=compressed+b'\xff'*(d['length']-len(compressed))
 out[0x749bfa:0x749bfc]=len(compressed).to_bytes(2,'little')
 out[-2:]=(sum(out[:-2])&65535).to_bytes(2,'little')
 allowed=set(range(start,end))|{0x749bfa,0x749bfb,len(out)-2,len(out)-1}
 diff={i for i,(a,b) in enumerate(zip(source,out)) if a!=b};assert diff<=allowed
 # All nine neighboring advertisements remain byte-for-byte intact.
 for i in range(13,23):
  if i==17:continue
  o=descriptor(source,i);assert out[o['start']:o['start']+o['length']]==source[o['start']:o['start']+o['length']]
 return bytes(out),dict(version='v0.34-TEST',rom_sha256=sha(out),base_sha256=BASE,checksum=f'{int.from_bytes(out[-2:],"little"):04X}',source=caption['source'],translation=caption['translation'],resource=17,descriptor='0x749BF6',allocation=['0x00DAEA','0x00ECA1'],old_compressed_bytes=d['length'],new_compressed_bytes=len(compressed),decoded_bytes=len(art),changed_rom_bytes=len(diff),changed_pixel_operations=len(changed_pixels),neighbor_assets_unchanged=9,code_and_text_tables_unchanged=True,unexpected_changes=0)
def main():
 p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('output',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
 r,q=build(a.rom.read_bytes());assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(r)
 if a.report:a.report.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(q,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
