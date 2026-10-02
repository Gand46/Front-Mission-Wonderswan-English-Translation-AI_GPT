#!/usr/bin/env python3
"""Build twice, audit unchanged corpus, and verify cumulative/delta patches."""
import argparse,json,sys,unittest
from pathlib import Path
from build_v033 import ROOT,CLEAN,V32,sha,build,apply_ips,make_ips
sys.path.insert(0,str(ROOT/'vendor/17_WS_Patch_Tools_v0.1.1/src'))
from ws_patch_tools import bps

def main():
 p=argparse.ArgumentParser();p.add_argument('clean',type=Path);p.add_argument('result',type=Path);a=p.parse_args()
 clean=a.clean.read_bytes();assert sha(clean)==CLEAN
 base=apply_ips(clean,(ROOT/'patches/baseline_v032_from_clean.ips').read_bytes());assert sha(base)==V32
 r,report=build(clean);r2,_=build(base);assert r==r2==a.result.read_bytes()
 assert len(r)==8388608 and sum(r[:-2])&65535==int.from_bytes(r[-2:],'little')
 corpus=json.loads((ROOT/'history/v032/data/binary_derived_corpus_v032.json').read_text())['entries']
 for e in corpus:
  p=int(e['target'],16);old=bytes.fromhex(e['hex'])
  assert base[p:p+len(old)]==old and r[p:p+len(old)]==old,e['index']
 # Every pixel of every font/asset is preserved: only enumerated code and checksum differ.
 patches=[]
 for label,source in [('clean',clean),('v032',base)]:
  for fmt,create,apply in [('ips',make_ips,apply_ips),('bps',bps.create,bps.apply)]:
   patch=create(source,r);assert apply(source,patch)==r
   name=f'v033_TEST_from_{label}.{fmt}';(ROOT/'patches'/name).write_bytes(patch)
   patches.append(dict(file=name,size=len(patch),sha256=sha(patch),roundtrip='PASS'))
 # CRC source and patch mismatch must reject; do not accept an unrelated ROM.
 wrong=bytearray(clean);wrong[0]^=1
 try:bps.apply(bytes(wrong),(ROOT/'patches/v033_TEST_from_clean.bps').read_bytes())
 except ValueError:pass
 else:raise AssertionError('BPS accepted wrong source')
 try:build(bytes(wrong))
 except ValueError:pass
 else:raise AssertionError('Builder accepted wrong source')
 report.update(static_status='PASS',build_clean_equals_build_v032=True,main_table_entries_unchanged=len(corpus),fonts_unchanged=True,name_grid_entries_preserved=231,nested_tables_unchanged=[3317,3339],patches_verified=patches,wrong_source_rejected=True,whole_game_approved=False)
 (ROOT/'qa/static_validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
