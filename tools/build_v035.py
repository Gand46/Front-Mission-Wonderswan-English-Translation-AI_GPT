"""Repair two near-pointer lists while preserving every main text byte sequence."""
import argparse,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from common import CLEAN_SHA256 as CLEAN, apply_ips, make_ips, sha256 as sha, text_target as target
from audit_japanese import parse
BASE='4d6a19c8a69c61edf92ccab3c17ec007f942faec66e6ffe7b68bdbb98450b263'
PT=0x7427c0
def raw(r,p):return bytes.fromhex(parse(r,p,{})['hex'])
def ptr(p):return struct.pack('<HH',p&65535,((p>>16)-0x70)<<12)
def build(source):
    spec=json.loads((ROOT/'data/repair.json').read_text())
    if sha(source)==CLEAN:
        # Ground reclaimed storage in four contiguous original scripts whose
        # current main aliases are all relocated. No guessed FF/code cave.
        for i,j in zip([3110,3111,3112,3113],[3111,3112,3113,3114]):
            assert target(source,i)+len(raw(source,target(source,i)))==target(source,j)
        assert target(source,3110)==0x7c9f48 and target(source,3114)==0x7ca0d1
        source=apply_ips(source,(ROOT/'patches/baseline_v034_from_clean.ips').read_bytes())
    if sha(source)!=BASE:raise ValueError('Expected exact clean Japanese ROM or canonical v0.34-TEST')
    start=int(spec['allocation']['start'],16);end=int(spec['allocation']['end_exclusive'],16)
    assert sha(source[start:end])==spec['allocation']['base_bytes_sha256']
    original={i:(target(source,i),raw(source,target(source,i))) for i in range(3358) if i not in (3317,3339)}
    for i,(p,b) in original.items():assert not(p<end and p+len(b)>start),('live text overlap',i)
    # Audit the four apparent far pointers into the reclaimed original region.
    found=[]
    for p in range(start,end):
        pos=0
        while (pos:=source.find(ptr(p),pos))>=0:found.append((pos,p));pos+=1
    assert set(found)=={(0x75ac1b,0x7ca002),(0x74c01b,0x7ca033),(0x79e5f5,0x7ca0c0),(0x79eba7,0x7ca0c0)}
    assert source[0x75ac17:0x75ac1f]==bytes.fromhex('c606873e02a000c0')
    for p in (0x79e5f4,0x79eba6):assert source[p:p+5]==bytes.fromhex('33c0a000c0')
    assert (0x74c01b-0x749b90)%6==1  # offset high byte / bank / length, not far pointer
    out=bytearray(source);cursor=start;allocations=[];allowed=set();moved={}
    def allocate(b,why,index):
        nonlocal cursor
        p=cursor;assert p+len(b)<=end and p>>16==(p+len(b)-1)>>16
        out[p:p+len(b)]=b;allowed.update(range(p,p+len(b)));cursor+=len(b)
        allocations.append(dict(index=index,start=hex(p),length=len(b),sha256=sha(b),purpose=why));return p
    for d in spec['relocate_dialogues']:
        p=int(d['old_target'],16);b=bytes.fromhex(d['bytes']);assert raw(source,p)==b
        aliases=[i for i in range(3358) if target(source,i)==p];assert aliases==d['aliases']
        new=allocate(b,'preserve dialogue overlapping old list sentinel',d['index']);moved[p]=new
        for i in aliases:
            at=PT+i*4;out[at:at+4]=ptr(new);allowed.update(range(at,at+4))
    tables=[]
    for t in spec['tables']:
        i=t['index'];p=target(source,i);assert p==int(t['target'],16)
        old=bytes.fromhex(t['expected_old_array']);assert source[p:p+len(old)]==old
        data=bytearray();children=[]
        for j in t['children']:
            origin,b=original[j];dest=origin
            if dest>>16!=p>>16:dest=allocate(b,'same-bank copy for near-pointer child',j)
            assert dest>>16==p>>16
            data+=(dest&65535).to_bytes(2,'little');children.append(dict(index=j,original_translation=hex(origin),near_target=hex(dest),copied=dest!=origin,sha256=sha(b)))
        data+=b'\xff\xff';assert len(data)==len(old)
        out[p:p+len(data)]=data;allowed.update(range(p,p+len(data)))
        tables.append(dict(index=i,target=hex(p),children=children,new_array=data.hex(' '),terminator='FFFF'))
    out[-2:]=(sum(out[:-2])&65535).to_bytes(2,'little');allowed.update(range(len(out)-2,len(out)))
    out=bytes(out)
    for i,(p,b) in original.items():assert raw(out,target(out,i))==b,('translation changed',i)
    for t in tables:
        p=target(out,t['index']);n=len(t['children'])
        for k,c in enumerate(t['children']):
            dest=(p&~65535)+struct.unpack_from('<H',out,p+2*k)[0]
            assert dest==int(c['near_target'],16) and raw(out,dest)==original[c['index']][1]
        assert out[p+2*n:p+2*n+2]==b'\xff\xff'
    changed={i for i,(a,b)in enumerate(zip(source,out))if a!=b};assert changed<=allowed
    pointer_changes=[i for i in range(3358)if source[PT+4*i:PT+4*i+4]!=out[PT+4*i:PT+4*i+4]]
    assert pointer_changes==[2928,3227,3228,3229,3230,3231,3232]
    report=dict(version='v0.35-TEST',base_sha256=BASE,rom_sha256=sha(out),rom_size=len(out),checksum=f'{int.from_bytes(out[-2:],"little"):04X}',main_text_entries_preserved=3356,changed_main_pointers=pointer_changes,secondary_roots_unchanged=True,secondary_children_repaired=25,sentinels_restored=2,same_bank_child_copies=6,translated_dialogues_relocated=2,allocation_start=hex(start),allocation_end_used=hex(cursor),allocation_capacity=end-start,allocation_bytes_used=cursor-start,allocations=allocations,tables=tables,changed_bytes=len(changed),unexpected_changes=0,translation_wording_changed=False,native_ending_scene_runtime='SYNTHETIC_STATE_PASS_SEPARATE_EVIDENCE',natural_full_campaign_ending='NOT_VALIDATED')
    return bytes(out),report
def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('output',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    out,q=build(a.rom.read_bytes());assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(out)
    if a.report:a.report.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in ('tables','allocations')},indent=2))
if __name__=='__main__':main()
