#!/usr/bin/env python3
"""Read-only v0.31 Japanese audit. No ROM mutations. Python standard library."""
import argparse, hashlib, json, re
from pathlib import Path
from collections import Counter, defaultdict

PT=0x7427C0
COUNT=3358
HASH='76d30792f9e82c74291c28864cdf4a86ee4e3e21fe0c2792a8f099b087234f4d'
BASE_HASH='d1d21d5199971b345e9907861c04a080ac7b44e07303f96717fd7f603f9ba380'
JP=re.compile('[\u3040-\u30ff\u3400-\u9fff]')
ONE=dict(zip(list(range(0x37,0x40))+list(range(0x73,0x80))+list(range(0xB7,0xBC))+list(range(0xBD,0xC0)), 'abcdefghijklmnopqrstuvwxyz .,!'))
# Verified by inspecting the extracted v0.31 glyph atlas, not by guessing Unicode.
JP_LABEL_CODES={f'C6:{x:02X}' for x in [0x41,0x42,0x43,0x44,0x47,0x48,0x4A,0x4C,0x4D,0x4E,0x50,0x51,0x52,0x53,0x54,0x55]}
NON_JP_SYMBOL_CODES={'C0:2F','C6:45','C6:49','C6:4F'}

def hx(n):return f'0x{n:06X}'
def target(r,i):
    p=PT+4*i; off=int.from_bytes(r[p:p+2],'little');seg=int.from_bytes(r[p+2:p+4],'little')
    assert 0x8000<=seg<=0xf000 and seg%0x1000==0
    return 0x700000+(seg>>12)*0x10000+off

def parse(r,start,table,production=True,limit=4096):
    p=start;parts=[];units=[];jps=[];unknown=[];end=False
    while p<min(len(r)-1,start+limit):
        pos=p;b=r[p];p+=1;raw=bytes([b]);kind='glyph';gid=b
        if b in (0xfa,0xfb,0xfe,0xff):
            kind='control';s={0xfa:'{NL}',0xfb:'{FB}',0xfe:'{BR}',0xff:'{END}'}[b]
            if b==0xff:end=True
        elif b in (0xf8,0xf9,0xfc,0xfd):
            raw=r[pos:p+1];p+=1;kind='control';s='{'+raw.hex(':').upper()+'}'
        else:
            if b>=0xc0:
                raw=r[pos:p+1];p+=1;gid=((b&15)+1)*0xc0+raw[1]
            s=ONE[b] if production and len(raw)==1 and b in ONE else table.get(raw)
            if s is None:s='{'+raw.hex(':').upper()+'}';unknown.append(raw.hex(':').upper())
            if JP.search(s):jps.append({'offset':hx(pos),'code':raw.hex(':').upper(),'text':s})
        parts.append(s);units.append((pos,kind,raw.hex(),gid,s))
        if end:break
    return dict(start=hx(start),end=hx(p),length=p-start,terminated=end,text=''.join(parts),japanese=jps,unknown=sorted(set(unknown)),hex=r[start:p].hex(' '),units=units)

def nested(r,p):
    # Conservative shape gate: >=3 increasing near pointers, first immediately after FFFF sentinel.
    vals=[];bank=p&0xff0000
    for k in range(128):
        w=int.from_bytes(r[p+2*k:p+2*k+2],'little')
        if w==0xffff:
            if len(vals)>=3 and vals[0]==p+2*k+2 and vals==sorted(set(vals)) and vals[-1]-p<0x8000:return vals
            return None
        vals.append(bank+w)
    return None

def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--clean',type=Path,required=True);ap.add_argument('--table',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    r=a.rom.read_bytes();b=a.clean.read_bytes();assert hashlib.sha256(r).hexdigest()==HASH;assert hashlib.sha256(b).hexdigest()==BASE_HASH
    a.out.mkdir(parents=True,exist_ok=True)
    td=json.loads(a.table.read_text());table={bytes.fromhex(x['code'].replace(':','')):x['unicode'] for x in td['entries']}
    tables={};rows=[];cache={};originals={};refs=defaultdict(list)
    for i in range(COUNT):
        p=target(r,i);q=target(b,i);refs[p].append(i)
        if q not in originals: originals[q]=parse(b,q,table,False)
        if (v:=nested(b,q)):tables[i]=v
        if p not in cache:cache[p]=parse(r,p,table)
        s=cache[p];old=originals[q]
        cat='LATIN_OR_NON_JP'
        if i in tables:cat='NESTED_NEAR_POINTER_TABLE'
        elif 709<=i<=939:cat='NAME_ENTRY_GRID'
        elif s['japanese']:cat='JAPANESE_PRESENT'
        elif set(s['unknown']) & JP_LABEL_CODES:cat='JAPANESE_ATTRIBUTE_LABELS'
        elif set(s['unknown'])-NON_JP_SYMBOL_CODES:cat='UNKNOWN_GLYPHS_REVIEW'
        elif not any(u[1]=='glyph' for u in s['units']):cat='CONTROL_ONLY'
        rows.append(dict(index=i,pointer_offset=hx(PT+4*i),target=hx(p),original_target=hx(q),pointer_changed=p!=q,category=cat,length=s['length'],text=s['text'],japanese_count=len(s['japanese']),japanese_label_codes=sorted(set(s['unknown'])&JP_LABEL_CODES),unknown=s['unknown'],unchanged_bytes=(r[p:p+s['length']]==b[q:q+old['length']]),hex=s['hex']))
    dump(a.out/'all_3358_entries.json',rows)
    nested_report=[]
    for i,vals in tables.items():
        q=target(b,i);p=target(r,i);n=len(vals);children=[]
        for k,v in enumerate(vals):
            newp=(p&0xff0000)+int.from_bytes(r[p+2*k:p+2*k+2],'little')
            old=parse(b,v,table,False);new=parse(r,newp,table)
            matching=[x for x in rows if x['original_target']==hx(v)]
            children.append(dict(subindex=k,original_target=hx(v),current_target=hx(newp),original_text=old['text'],current_text=new['text'],current_japanese_count=len(new['japanese']),main_table_aliases=refs.get(newp,[]),relocated_main_entries=[{'index':x['index'],'target':x['target'],'text':x['text']} for x in matching],bytes_unchanged=b[v:v+old['length']]==r[newp:newp+new['length']]))
        nested_report.append(dict(index=i,table_target=hx(p),count=n,original_hex=b[q:q+2*n+2].hex(' '),current_hex=r[p:p+2*n+2].hex(' '),sentinel_intact=r[p+2*n:p+2*n+2]==b'\xff\xff',children=children))
    dump(a.out/'nested_tables.json',nested_report)
    suspects=[x for x in rows if x['category'] in ['JAPANESE_PRESENT','JAPANESE_ATTRIBUTE_LABELS','UNKNOWN_GLYPHS_REVIEW']]
    dump(a.out/'japanese_and_unknown_candidates.json',suspects)
    # Retention of original main-table scripts. Presence is NOT proof of runtime use.
    retention=[]
    for p,s in originals.items():
        if len(s['japanese'])<3 or s['length']<6 or s['length']>2048 or nested(b,p):continue
        raw=b[p:p+s['length']];pos=r.find(raw);hits=[]
        while pos>=0 and len(hits)<64:
            hits.append({'offset':hx(pos),'main_indices':refs.get(pos,[]) });pos=r.find(raw,pos+1)
        if hits:retention.append({'clean_offset':hx(p),'original_text':s['text'],'length':s['length'],'hits':hits})
    dump(a.out/'original_japanese_retained.json',retention)
    # Whole-ROM search for exact text-style far pointer signatures to retained scripts.
    retained_targets={int(h['offset'],16) for s in retention for h in s['hits']}
    far_hits=[];outside=[]
    for match in re.finditer(b'(?=(..\x00[\x80\x90\xa0\xb0\xc0\xd0\xe0\xf0]))',r,re.S):
        raw=match.group(1);pos=match.start();dest=0x700000+(raw[3]>>4)*65536+int.from_bytes(raw[:2],'little')
        if dest in retained_targets:
            row={'offset':hx(pos),'target':hx(dest),'inside_main_table':PT<=pos<PT+COUNT*4,'warning':'byte-pattern candidate; consumer not proven'}
            far_hits.append(row)
            if not row['inside_main_table']:outside.append(row)
    dump(a.out/'retained_text_far_pointer_candidates.json',far_hits)
    summary=dict(rom_sha256=HASH,clean_sha256=BASE_HASH,entries=COUNT,unique_targets=len(cache),categories=dict(Counter(x['category'] for x in rows)),japanese_attribute_glyph_types=len(JP_LABEL_CODES),japanese_attribute_unique_targets=len({x['target'] for x in rows if x['category']=='JAPANESE_ATTRIBUTE_LABELS'}),nested_tables=len(tables),nested_children=sum(map(len,tables.values())),retained_original_japanese_records=len(retention),retained_original_unique_byte_strings=len({b[int(x['clean_offset'],16):int(x['clean_offset'],16)+x['length']] for x in retention}),retained_records_without_main_references=sum(not any(y['main_indices'] for y in x['hits']) for x in retention),outside_main_far_pointer_pattern_hits=len(outside),not_a_whole_game_completion_percentage=True,notes=['Decoder follows 0x781F77..0x78201A; FD handled as special control/glyph, not normal JP.','Japanese grid is retained separately. Near-pointer arrays must not be rendered as dialogue.','Original Japanese bytes without proven consumers are not confirmed untranslated gameplay.','Attribute labels classified from direct glyph pixels: see unknown_glyph_atlas.png.'])
    dump(a.out/'summary.json',summary);print(json.dumps(summary,indent=2))
    for row in suspects:
        if row['category']=='JAPANESE_PRESENT':print(row['index'],row['category'],row['text'][:200])

if __name__=='__main__':main()
