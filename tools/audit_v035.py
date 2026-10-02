import argparse,json,struct,sys
from pathlib import Path
from build_v035 import ROOT,BASE,CLEAN,PT,build,raw,target,sha,apply_ips,make_ips
from resources import descriptor
sys.path.insert(0,str(ROOT/'vendor/17_WS_Patch_Tools_v0.1.1/src'))
from ws_patch_tools import bps
EXPECTED='bed365a706e13338c8bebc17723fc40f3804a114520524d3ad62f180d44f42c0'
def dump(name,q):(ROOT/'qa'/name).write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('clean',type=Path);ap.add_argument('rom',type=Path);a=ap.parse_args()
    clean=a.clean.read_bytes();r=a.rom.read_bytes();assert sha(clean)==CLEAN and sha(r)==EXPECTED
    base=apply_ips(clean,(ROOT/'patches/baseline_v034_from_clean.ips').read_bytes());assert sha(base)==BASE
    rebuilt,report=build(clean);assert rebuilt==r and build(base)[0]==r
    texts=[]
    for i in range(3358):
        if i in (3317,3339):continue
        before=raw(base,target(base,i));after=raw(r,target(r,i));assert before==after
        texts.append(dict(index=i,old_target=hex(target(base,i)),new_target=hex(target(r,i)),length=len(after),sha256=sha(after),byte_sequence_identical=True))
    dump('all_text_preservation.json',texts)
    gfx=[]
    for t,n in [(0x740130,483),(0x749b90,1616),(0x74d290,873)]:
        assert r[t:t+6*n]==base[t:t+6*n]
        for i in range(n):
            d=descriptor(base,i,t);s=d['start'];e=s+d['length'];assert r[s:e]==base[s:e],(hex(t),i)
        gfx.append(dict(table=hex(t),descriptors=n,all_descriptors_and_payloads_identical=True))
    dump('graphics_preservation.json',gfx)
    retired=[]
    for i in [3110,3111,3112,3113]:
        p=target(clean,i);b=raw(clean,p);aliases=[j for j in range(3358)if target(clean,j)==p]
        retired.append(dict(original_index=i,original_target=hex(p),original_length=len(b),original_sha256=sha(b),original_aliases=aliases,current_targets=[hex(target(base,j))for j in aliases],all_aliases_relocated=all(target(base,j)!=p for j in aliases)))
    assert all(q['all_aliases_relocated']for q in retired);dump('reclaimed_source_provenance.json',retired)
    # Every apparent direct far pointer to the relocated English starts must
    # be one of the main aliases explicitly updated by the repair.
    alias_refs=[]
    for d in json.loads((ROOT/'data/repair.json').read_text())['relocate_dialogues']:
        p=int(d['old_target'],16);needle=struct.pack('<HH',p&65535,0xc000);pos=0;hits=[]
        while(pos:=base.find(needle,pos))>=0:hits.append(pos);pos+=1
        expected=[PT+4*i for i in d['aliases']];assert hits==expected
        alias_refs.append(dict(old_target=hex(p),reference_offsets=[hex(x)for x in hits],all_are_updated_main_aliases=True))
    dump('relocated_dialogue_references.json',alias_refs)
    patches=[]
    for name,src in [('clean',clean),('v034',base)]:
        for ext,maker,apply in [('bps',bps.create,bps.apply),('ips',make_ips,apply_ips)]:
            blob=maker(src,r);assert apply(src,blob)==r
            fn=f'v035_TEST_from_{name}.{ext}';(ROOT/'patches'/fn).write_bytes(blob)
            patches.append(dict(file=fn,size=len(blob),sha256=sha(blob),roundtrip='PASS'))
    report.update(build_from_clean='PASS',build_from_v034='PASS',preserved_graphics_descriptors=2972,all_graphics_payloads_preserved=True,patches=patches,whole_game_translation_approved=False)
    dump('static_validation.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ('tables','allocations','patches')},indent=2))
if __name__=='__main__':main()
