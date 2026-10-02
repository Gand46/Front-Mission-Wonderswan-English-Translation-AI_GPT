"""Scoped text/asset inventory. Never infer global translation completion."""
import argparse,json,re,sys
from collections import Counter
from pathlib import Path
from build_v034 import ROOT,BASE,sha,build,apply_ips,make_ips,CLEAN
from resources import descriptor,decode
OLD=ROOT/'history/v033/history/v032'
sys.path.insert(0,str(OLD/'tools'))
from audit_japanese import parse,target,nested,JP
sys.path.insert(0,str(ROOT/'history/v033/vendor/17_WS_Patch_Tools_v0.1.1/src'))
from ws_patch_tools import bps
def dump(name,obj):(ROOT/'qa'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('clean',type=Path);p.add_argument('rom',type=Path);a=p.parse_args()
 clean=a.clean.read_bytes();r=a.rom.read_bytes();assert sha(clean)==CLEAN
 base=apply_ips(clean,(ROOT/'patches/baseline_v033_from_clean.ips').read_bytes());assert sha(base)==BASE
 assert build(clean)[0]==build(base)[0]==r
 assert len(r)==8388608 and sum(r[:-2])&65535==int.from_bytes(r[-2:],'little')
 table={bytes.fromhex(e['code'].replace(':','')):e['unicode'] for e in json.loads((OLD/'data/wsc_unicode_table_v0.13.json').read_text())['entries']}
 labels=json.loads((OLD/'data/translations_v032.json').read_text())['labels']
 table.update({bytes.fromhex(e['code'].replace(':','')):'['+e['label']+']' for e in labels})
 rows=[];jp=[];unknown=[];special={'C0:2F','C6:45','C6:49','C6:4F'}
 for i in range(3358):
  s=target(r,i);assert s==target(base,i)
  if i in (3317,3339):
   n=7 if i==3317 else 18
   assert r[s:s+2*n+2]==base[s:s+2*n+2]
   rows.append(dict(index=i,status='NEEDS_CONSUMER_TRACE',children=n,target=hex(s)));continue
  q=parse(r,s,table);old=parse(base,s,table);assert q['hex']==old['hex']
  status='NAME_ENTRY_GRID_PRESERVED' if 709<=i<=939 else 'NO_JP_DETECTED_IN_MAPPED_TEXT'
  if status!='NAME_ENTRY_GRID_PRESERVED':
   if q['japanese']:jp.append(i)
   if set(q['unknown'])-special:unknown.append(i)
  rows.append(dict(index=i,target=hex(s),status=status,text=q['text'],japanese=q['japanese'],unknown=q['unknown']))
 dump('main_text_audit.json',rows)
 # Original retained strings: their presence is not evidence of a live consumer.
 originals={};retained=[];targets=set()
 for i in range(3358):
  if 709<=i<=939 or i in (3317,3339):continue
  s=target(clean,i)
  if s in originals:continue
  q=parse(clean,s,table,False);originals[s]=q
  if len(q['japanese'])<3 or not q['terminated'] or not 6<=q['length']<=2048:continue
  raw=clean[s:s+q['length']];hits=[];pos=r.find(raw)
  while pos>=0:
   hits.append(hex(pos));targets.add(pos);pos=r.find(raw,pos+1)
  if hits:retained.append(dict(original_target=hex(s),original_text=q['text'],hits=hits,status='RETAINED_BYTES_RUNTIME_UNPROVEN'))
 dump('retained_original_text_candidates.json',retained)
 far=[]
 for m in re.finditer(b'(?=(..\x00[\x80\x90\xa0\xb0\xc0\xd0\xe0\xf0]))',r,re.S):
  raw=m.group(1);dest=0x700000+(raw[3]>>4)*65536+int.from_bytes(raw[:2],'little')
  if dest in targets:far.append(dict(offset=hex(m.start()),target=hex(dest),inside_main_table=0x7427c0<=m.start()<0x745c38,status='BYTE_PATTERN_NOT_PROVEN_POINTER'))
 dump('retained_text_pointer_candidates.json',far)
 # Grounded table: 1616 consecutive valid descriptors; next bytes are not a descriptor.
 inventory=[]
 reviewed={3:'world map tiles',7:'Latin location labels',10:'English advertisement header',32:'English UI tiles',33:'English UI tiles',40:'English combat UI tiles',1214:'English machine-selection UI tiles'}
 for i in range(1616):
  d=descriptor(r,i);assert 0x80<=d['bank']<=0xff and d['length']>0
  s=d['start'];assert s+d['length']<=len(r)
  d.update(start=hex(s),sha256=sha(r[s:s+d['length']]),status='INVENTORIED_NOT_GLOBALLY_REVIEWED')
  try:
   decoded,end=decode(r,s,32768)
   d.update(strict_rle=end==s+d['length'],decoded_bytes=len(decoded) if end==s+d['length'] else None)
  except (ValueError,IndexError):d.update(strict_rle=False,decoded_bytes=None)
  if i in reviewed:d.update(status='STATIC_TILE_REVIEW_NO_JP_OBSERVED',review=reviewed[i])
  if 13<=i<=22:d.update(status='NATURAL_RUNTIME_VISUAL_REVIEW_NO_JP',review='All ten advertisements; source 17 translated this version')
  inventory.append(d)
 assert not 0x80<=descriptor(r,1616)['bank']<=0xff
 dump('graphics_resource_inventory.json',inventory)
 patches=[]
 for name,src in [('clean',clean),('v033',base)]:
  for ext,maker,apply in [('bps',bps.create,bps.apply),('ips',make_ips,apply_ips)]:
   b=maker(src,r);assert apply(src,b)==r
   fn=f'v034_TEST_from_{name}.{ext}';(ROOT/'patches'/fn).write_bytes(b);patches.append(dict(file=fn,size=len(b),sha256=sha(b),roundtrip='PASS'))
 assert not jp and not unknown
 summary=dict(version='v0.34-TEST',rom_sha256=sha(r),clean_sha256=CLEAN,main_table_entries=3358,mapped_text_entries=3125,japanese_detected_in_mapped_text=jp,unclassified_glyph_entries=unknown,preserved_name_grid_entries=231,nested_tables_needing_context=[3317,3339],nested_children=25,graphics_descriptors_inventoried=len(inventory),strict_rle_candidates=sum(x['strict_rle'] for x in inventory),advertisements_reviewed_in_natural_runtime=10,japanese_remaining_in_those_advertisements=0,retained_original_strings=len(retained),outside_main_pointer_patterns=sum(not x['inside_main_table'] for x in far),patches=patches,whole_game_no_japanese_claim=False,global_status='NOT_APPROVED_GLOBAL_COVERAGE_INCOMPLETE')
 dump('audit_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
