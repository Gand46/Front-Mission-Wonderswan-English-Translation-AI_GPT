#!/usr/bin/env python3
"""Reproducible v0.32-TEST. Standard library; no ROM is distributed."""
import argparse, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = 'd1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380'
V31 = '76d30792f9e82c74291c28864cdf4a86ee4e3e21fe0c2792a8f099b087234f4d'
PT = 0x7427C0
ONE = dict(zip('abcdefghijklmnopqrstuvwxyz .,!', list(range(0x37,0x40))+list(range(0x73,0x80))+list(range(0xB7,0xBC))+list(range(0xBD,0xC0))))
# Editable 3x7 pixel letters. Two letters fit in the existing 8-pixel advance.
FONT = {
 'A':['010','101','101','111','101','101','101'],
 'C':['011','100','100','100','100','100','011'],
 'D':['110','101','101','101','101','101','110'],
 'E':['111','100','100','110','100','100','111'],
 'F':['111','100','100','110','100','100','100'],
 'G':['011','100','100','101','101','101','011'],
 'L':['100','100','100','100','100','100','111'],
 'M':['101','111','111','101','101','101','101'],
 'P':['110','101','101','110','100','100','100'],
 'R':['110','101','101','110','101','101','101'],
 'S':['011','100','100','010','001','001','110'],
 'T':['111','010','010','010','010','010','010'],
 'V':['101','101','101','101','101','101','010'],
 'W':['101','101','101','101','111','111','101'],
}

def sha(b): return hashlib.sha256(b).hexdigest()

def apply_ips(base, patch):
    if patch[:5] != b'PATCH': raise ValueError('Invalid IPS header')
    out=bytearray(base);p=5
    while True:
        if p+3>len(patch): raise ValueError('Truncated IPS')
        if patch[p:p+3]==b'EOF':
            if p+3 != len(patch): raise ValueError('Unexpected IPS trailer')
            return bytes(out)
        off=int.from_bytes(patch[p:p+3],'big');p+=3
        if p+2>len(patch): raise ValueError('Truncated IPS size')
        n=int.from_bytes(patch[p:p+2],'big');p+=2
        if n:
            data=patch[p:p+n];p+=n
            if len(data)!=n: raise ValueError('Truncated IPS data')
        else:
            if p+3>len(patch): raise ValueError('Truncated IPS RLE')
            n=int.from_bytes(patch[p:p+2],'big');data=bytes([patch[p+2]])*n;p+=3
        if off+n>len(out): raise ValueError('IPS exceeds ROM')
        out[off:off+n]=data

def make_ips(base, modified):
    if len(base)!=len(modified): raise ValueError('ROM size changed')
    out=bytearray(b'PATCH');p=0
    while p<len(base):
        if base[p]==modified[p]:p+=1;continue
        start=p
        # IPS has a reserved EOF offset. Include its preceding equal byte.
        if start==0x454F46:start-=1
        while p<len(base) and base[p]!=modified[p] and p-start<65535:p+=1
        data=modified[start:p]
        out+=start.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data
    return bytes(out+b'EOF')

def target(r,i):
    p=PT+4*i;off=int.from_bytes(r[p:p+2],'little');seg=int.from_bytes(r[p+2:p+4],'little')
    if seg not in range(0x8000,0x10000,0x1000):raise ValueError('Unexpected segment')
    return 0x700000+(seg>>12)*65536+off

def glyph_offset(r,g):
    s=int.from_bytes(r[0x782EE9+(g>>6)*2:0x782EEB+(g>>6)*2],'little');d=0x740130+s*6
    return ((r[d+2]&127)<<16)+int.from_bytes(r[d:d+2],'little')+(g&63)*128

def decode_pixels(data):
    a=[[6]*16 for _ in range(16)]
    for t,(dy,dx) in enumerate(((0,0),(0,8),(8,0),(8,8))):
        for y in range(8):
            for x in range(4):
                v=data[t*32+y*4+x];a[dy+y][dx+2*x]=v>>4;a[dy+y][dx+2*x+1]=v&15
    return a

def encode_pixels(a):
    return bytes((a[dy+y][dx+x]<<4)|a[dy+y][dx+x+1]
                 for dy,dx in ((0,0),(0,8),(8,0),(8,8)) for y in range(8) for x in range(0,8,2))

def label_pixels(label):
    if not 1<=len(label)<=2:raise ValueError('At most two letters per glyph')
    a=[[6]*16 for _ in range(16)];points=set();start=0 if len(label)==2 else 2
    for k,ch in enumerate(label):
        for y,row in enumerate(FONT[ch]):
            for x,v in enumerate(row):
                if v=='1':points.add((start+4*k+x,y+2))
    for x,y in points:
        for dx,dy in ((1,0),(0,1),(1,1)):a[y+dy][x+dx]=9
    for x,y in points:a[y][x]=1
    return encode_pixels(a)

def build(v31, manifest):
    if len(v31)!=8388608 or sha(v31)!=V31:raise ValueError('Expected canonical v0.31')
    out=bytearray(v31);allowed=set();changes=[]
    for item in manifest['labels']:
        tail=int(item['code'].split(':')[1],16);p=glyph_offset(v31,7*192+tail)
        if p!=int(item['offset'],16) or sha(v31[p:p+128])!=item['original_sha256']:
            raise ValueError('Glyph baseline mismatch')
        data=label_pixels(item['label']);out[p:p+128]=data;allowed.update(range(p,p+128))
        changes.append({**item,'new_sha256':sha(data)})
    # Repack ONLY the contiguous five test records, never use guessed free space.
    tests=manifest['tests'];start=int(tests[0]['original_target'],16);cursor=start
    for item in tests:
        old=bytes.fromhex(item['original_hex']);p=int(item['original_target'],16)
        if p!=cursor or target(v31,item['index'])!=p or v31[p:p+len(old)]!=old:
            raise ValueError('Unexpected test-record layout')
        signature=v31[PT+4*item['index']:PT+4*item['index']+4]
        hits=[];pos=v31.find(signature)
        while pos>=0:hits.append(pos);pos=v31.find(signature,pos+1)
        if hits!=[PT+4*item['index']]:raise ValueError('Additional far reference needs review')
        cursor+=len(old)
    end=cursor
    if any(start<=target(v31,i)<end for i in range(3358) if i not in {x['index'] for x in tests}):
        raise ValueError('Unexpected alias to test region')
    out[start:end]=b'\xff'*(end-start);allowed.update(range(start,end));cursor=start;test_changes=[]
    for item in tests:
        data=bytes.fromhex('fc01c03afe')+bytes(ONE[c] for c in item['translation'])+b'\xff'
        if cursor+len(data)>end:raise ValueError('Test translations exceed reclaimed block')
        p=PT+4*item['index'];out[p:p+2]=(cursor&65535).to_bytes(2,'little');allowed.update(range(p,p+2))
        out[cursor:cursor+len(data)]=data
        test_changes.append({**item,'new_target':f'0x{cursor:06X}','new_hex':data.hex(' ')})
        cursor+=len(data)
    # Preserve the record's existing allocation, but start on the next bank.
    fix=manifest['bank_boundary_fix'];i=fix['index'];p=target(v31,i)
    old=bytes.fromhex(fix['original_hex']);end=p+len(old);dest=int(fix['new_target'],16)
    if p!=int(fix['original_target'],16) or v31[p:end]!=old or not p<dest<end:
        raise ValueError('Bank-boundary record baseline mismatch')
    if any(p<=target(v31,j)<end for j in range(3358) if j!=i):raise ValueError('Shared bank-boundary allocation')
    sig=v31[PT+4*i:PT+4*i+4]
    if v31.count(sig)!=1:raise ValueError('Additional reference to bank-boundary record')
    td=json.loads((ROOT/'data/wsc_unicode_table_v0.13.json').read_text(encoding='utf-8'))
    enc={x['unicode']:bytes.fromhex(x['code'].replace(':','')) for x in td['entries']}
    # The legacy table also has FD alternate-width aliases: use ordinary capitals.
    enc.update({chr(65+k):bytes((0xC0,0x40+k)) for k in range(26)})
    enc.update({ch:bytes([code]) for ch,code in ONE.items()})
    data=b'\xfe'.join(b''.join(enc[c] for c in part) for part in fix['translation'].split('{BR}'))+b'\xff'
    if dest+len(data)>end or dest//65536!=(dest+len(data)-1)//65536:raise ValueError('Boundary fix does not fit')
    out[dest:end]=data+b'\xff'*(end-dest-len(data));allowed.update(range(dest,end))
    pp=PT+4*i;out[pp:pp+4]=(dest&65535).to_bytes(2,'little')+(((dest>>16)-0x70)<<12).to_bytes(2,'little');allowed.update(range(pp,pp+4))
    boundary_change={**fix,'new_hex':data.hex(' '),'bytes_used':len(data),'bytes_available':end-dest}
    out[-2:]=(sum(out[:-2])&65535).to_bytes(2,'little');allowed.update((len(out)-2,len(out)-1))
    changed=[i for i,(a,b) in enumerate(zip(v31,out)) if a!=b]
    if not set(changed)<=allowed:raise ValueError('Change outside whitelist')
    return bytes(out),dict(labels=changes,tests=test_changes,bank_boundary_fix=boundary_change,changed_bytes=len(changed),rom_sha256=sha(out),checksum=f'0x{int.from_bytes(out[-2:],"little"):04X}',whitelist_check='PASS')

def main():
    p=argparse.ArgumentParser();p.add_argument('rom',type=Path);p.add_argument('output',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    source=a.rom.read_bytes()
    if sha(source)==CLEAN:source=apply_ips(source,(ROOT/'patches/baseline_v031_from_clean.ips').read_bytes())
    manifest=json.loads((ROOT/'data/translations_v032.json').read_text(encoding='utf-8'))
    result,report=build(source,manifest)
    if a.output.exists():raise SystemExit('Output already exists; choose a new filename.')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result)
    if a.report:a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('BUILD PASS (static only)');print('SHA-256:',sha(result));print('Checksum:',report['checksum'])

if __name__=='__main__':main()
