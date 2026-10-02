import argparse,json
from pathlib import Path
from PIL import Image,ImageChops
from build_v034 import ROOT,sha
from resources import decode,descriptor
p=argparse.ArgumentParser();p.add_argument('rom',type=Path);a=p.parse_args();r=a.rom.read_bytes()
report=json.loads((ROOT/'qa/ads_after/final.json').read_text());events=json.loads((ROOT/'qa/ads_after/final.lua.json').read_text())
assert report['rom_sha256']==sha(r) and report['passed'] and not report['timed_out'] and report['process_exit']==0
assert events['natural_ad_captures']==10 and not events['memory_injection'] and all(v>=3 for v in events['descriptor_reads'].values())
vram=(ROOT/'qa/ads_after/sakata_vram.bin').read_bytes();raw,end=decode(r,descriptor(r,17)['start']);assert raw==vram
before=Image.open(ROOT/'qa/before/sakata_v033_NATURAL.png').convert('RGB')
after=Image.open(ROOT/'qa/ads_after/ad_17_frame_10500_NATURAL.png').convert('RGB')
diff=ImageChops.difference(before,after);box=diff.getbbox();assert box==(55,123,168,141)
assert diff.crop((0,0,237,123)).getbbox() is None
q=dict(rom_sha256=sha(r),mesen_sha256=report['mesen_sha256'],natural_frames=events['frames'],advertisements=10,injection=False,all_ten_descriptors_read=True,sakata_rom_decode_equals_captured_vram=True,vram_sha256=sha(vram),changed_screen_bbox_exclusive=box,other_screen_pixels_unchanged=True,visual_review='All 10 natural screenshots examined; captions English; no clipping observed',linguistic_review=dict(source='新発売!!',translation='NEW RELEASE!!',context='new product advertisement',status='APPROVED_FOR_THIS_CAPTION'),global_approval=False)
(ROOT/'qa/runtime_validation.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps(q,ensure_ascii=False,indent=2))
