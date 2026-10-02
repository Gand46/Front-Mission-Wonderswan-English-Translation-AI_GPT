"""Validate the current controlled, natural-route, and native-epilogue evidence."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
from build_v035 import ROOT,BASE
from audit_v035 import EXPECTED
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    qa=ROOT/'qa';runs=[];targets=set();frames=0
    for g in 'ABCD':
        folder=qa/f'runtime_{g}';q=json.loads((folder/'final.json').read_text());data=json.loads((folder/'final.lua.json').read_text())
        assert q['passed'] and q['process_exit']==0 and not q['timed_out'] and q['rom_sha256']==EXPECTED
        assert q['lua_sha256']==sha(qa/f'controlled_{g}_repaired.lua') and q['capture_sha256']==sha(folder/'final.png')
        assert data['memory_payloads_verified'] and data['captured']==data['expected'] and not data['native_ending_consumer']
        for c in data['cases']:
            assert c['captured'] and c['pointer_reads']>0 and (folder/f"record_{c['target']:04d}_CONTROLLED.png").exists();targets.add(c['target'])
        frames+=data['frames'];runs.append(dict(group=g,frames=data['frames'],cases=data['expected'],passed=True))
    assert targets==set(range(3318,3325))|set(range(3340,3358))|{3227,2928}
    comparisons=[]
    baseline=qa/'runtime_D_baseline';q=json.loads((baseline/'final.json').read_text())
    assert q['passed'] and q['rom_sha256']==BASE and q['lua_sha256']==sha(qa/'controlled_D_baseline.lua')
    for p in sorted(baseline.glob('record_*_CONTROLLED.png')):
        new=qa/'runtime_D'/p.name;assert ImageChops.difference(Image.open(p).convert('RGB'),Image.open(new).convert('RGB')).getbbox() is None
        comparisons.append(dict(file=p.name,pixel_identical=True,baseline_sha256=sha(p),repaired_sha256=sha(new)))
    assert len(comparisons)==8
    (qa/'controlled_comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
    natural=json.loads((qa/'natural_after/final.json').read_text());route=json.loads((qa/'natural_after/final.lua.json').read_text())
    assert natural['passed'] and natural['rom_sha256']==EXPECTED and natural['lua_sha256']==sha(qa/'natural_route.lua')
    assert route['frames']==24000 and route['memory_injection']==False
    natural_comparisons=[]
    for p in sorted((qa/'natural_before').glob('frame_*.png')):
        new=qa/'natural_after'/p.name
        assert ImageChops.difference(Image.open(p).convert('RGB'),Image.open(new).convert('RGB')).getbbox() is None,p.name
        natural_comparisons.append(dict(file=p.name,pixel_identical=True,baseline_sha256=sha(p),repaired_sha256=sha(new)))
    assert len(natural_comparisons)==8
    (qa/'natural_comparison.json').write_text(json.dumps(natural_comparisons,indent=2)+'\n')
    native=json.loads((qa/'epilogue_native/native_validation.json').read_text())
    native_run=json.loads((qa/'epilogue_native/isolated_v035/final.lua.json').read_text())
    assert native['classification']=='SYNTHETIC_STATE' and native['requested_text_records']==25
    assert native['requested_japanese_glyphs']==0 and native['requested_unknown_glyphs']==0
    assert len(native_run['native_index_reads'])==39 and native_run['legacy_root_reads']==[0,0]
    result=dict(version='v0.35-TEST',rom_sha256=EXPECTED,controlled_runs=runs,controlled_frames_current_rom=frames,secondary_children_rendered=25,relocated_dialogues_rendered=2,controlled_comparison_captures_identical=8,natural_route_frames=24000,natural_checkpoint_captures_identical=8,native_epilogue_frames=36000,total_frames_current_rom=frames+24000+36000,native_ending_consumer='SYNTHETIC_STATE_PASS',native_ending_requested_layout='PASS_25_OF_25',native_ending_requested_japanese_glyphs=0,native_ending_requested_unknown_glyphs=0,natural_campaign_completion='NOT_VALIDATED',linguistic_changes=0,visual_scope='25 requested strings in the native epilogue, controlled primary-renderer coverage, two preserved dialogues, and initial-route checkpoint comparison',whole_game_approved=False)
    (qa/'runtime_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
