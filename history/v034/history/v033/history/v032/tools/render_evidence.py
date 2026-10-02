#!/usr/bin/env python3
"""Extract glyph pixels directly; these are static atlas views, not emulator captures."""
import argparse,json,math,hashlib
from pathlib import Path
from collections import Counter
from PIL import Image,ImageDraw
from audit_japanese import parse,target,ONE,JP_LABEL_CODES,BASE_HASH,HASH

def glyph_off(r,g):
    s=int.from_bytes(r[0x782ee9+(g>>6)*2:0x782eeb+(g>>6)*2],'little');d=0x740130+s*6
    return ((r[d+2]&127)<<16)+int.from_bytes(r[d:d+2],'little')+(g&63)*128
def glyph_image(r,g):
    p=glyph_off(r,g);raw=r[p:p+128];a=[[0]*16 for _ in range(16)]
    for t,(dy,dx) in enumerate([(0,0),(0,8),(8,0),(8,8)]):
        for y in range(8):
            for x in range(4):
                v=raw[t*32+y*4+x];a[dy+y][dx+x*2]=v>>4;a[dy+y][dx+x*2+1]=v&15
    bg=Counter(v for row in a for v in row).most_common(1)[0][0];im=Image.new('RGB',(16,16))
    im.putdata([(18,24,34) if v==bg else (247,249,252) if v==1 else (80,98,117) for row in a for v in row]);return im
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rom',required=True,type=Path);ap.add_argument('--clean',type=Path);ap.add_argument('--table',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();r=a.rom.read_bytes();assert hashlib.sha256(r).hexdigest()==HASH;a.out.mkdir(exist_ok=True,parents=True)
    table={bytes.fromhex(x['code'].replace(':','')):x['unicode'] for x in json.loads(a.table.read_text())['entries']}
    rows=json.loads((a.out/'all_3358_entries.json').read_text());codes=sorted(set(c for x in rows if x['category'] not in ['NAME_ENTRY_GRID','NESTED_NEAR_POINTER_TABLE'] for c in x['unknown']))
    im=Image.new('RGB',(720,70+math.ceil(len(codes)/6)*104),(18,24,34));d=ImageDraw.Draw(im);d.text((15,15),'v0.31: every unknown glyph outside Name Entry / nested tables',fill='white');d.text((15,33),'Direct ROM pixels; static atlas, NOT runtime evidence.',fill='white')
    for j,c in enumerate(codes):
        raw=bytes.fromhex(c.replace(':',''));g=raw[0] if len(raw)==1 else ((raw[0]&15)+1)*192+raw[1];x=j%6*120+20;y=65+j//6*104
        d.text((x,y),c,fill='yellow');im.paste(glyph_image(r,g).resize((64,64),Image.Resampling.NEAREST),(x,y+19))
    im.save(a.out/'unknown_glyph_atlas.png')
    im=Image.new('RGB',(840,400),(18,24,34));d=ImageDraw.Draw(im);d.text((15,12),'Five retained test strings: static v0.31 font rendering (not runtime)',fill='white')
    for k,i in enumerate(range(2099,2104)):
        s=parse(r,target(r,i),table);y=45+k*68;d.text((12,y),f'{i} @ {s["start"]}   FC:01 name placeholder omitted',fill='yellow');x=20
        for _,kind,_,g,_ in s['units']:
            if kind=='glyph':im.paste(glyph_image(r,g).resize((32,32),Image.Resampling.NEAREST),(x,y+20));x+=32
    im.save(a.out/'test_strings_static.png')
    samples=[137,138,139,545,496,674]
    im=Image.new('RGB',(1080,70+len(samples)*110),(18,24,34));d=ImageDraw.Draw(im);d.text((15,10),'v0.31 English descriptions retaining Japanese attribute glyphs',fill='white');d.text((15,27),'Static glyph strips / 16 px cells; NOT game layout or runtime screenshots.',fill='white');d.text((15,44),'FD special-width operators and dynamic FC values omitted from these strips.',fill='white')
    for k,i in enumerate(samples):
        s=parse(r,target(r,i),table);y=65+k*110;d.text((12,y),f'Index {i} @ {s["start"]}',fill='yellow');x=15;y+=20
        for _,kind,raw,g,label in s['units']:
            if raw in ('fa','fe'):x=15;y+=34
            if kind=='glyph':
                if x>1030:x=15;y+=34
                im.paste(glyph_image(r,g).resize((32,32),Image.Resampling.NEAREST),(x,y));x+=32
    im.save(a.out/'attribute_examples_static.png')
    if a.clean:
        b=a.clean.read_bytes();assert hashlib.sha256(b).hexdigest()==BASE_HASH
        legacy={c:0xc0+i for i,c in enumerate('abcdefghijklmnopqrstuvwxyz')};legacy.update({' ':0xff,'.':0xf6,',':0xf5,'!':0xf8})
        aliases=[]
        for code,ch in ONE.items():
            p=glyph_off(r,code);q=glyph_off(r,legacy[ch]);same=r[p:p+128]==r[q:q+128];assert same
            aliases.append({'code':f'{code:02X}','character':ch,'pixel_bytes_match_legacy':same})
        labels=[]
        for code in sorted(JP_LABEL_CODES):
            g=7*192+int(code.split(':')[1],16);p=glyph_off(r,g);q=glyph_off(b,g);same=r[p:p+128]==b[q:q+128];assert same
            labels.append({'code':code,'glyph_id':hex(g),'offset':f'0x{p:06X}','identical_to_japanese_original':same,'sha256':hashlib.sha256(r[p:p+128]).hexdigest(),'referencing_entries':[x['index'] for x in rows if code in x['unknown'] and x['category']=='JAPANESE_ATTRIBUTE_LABELS']})
        (a.out/'glyph_verification.json').write_text(json.dumps({'one_byte_aliases':aliases,'japanese_attribute_labels':labels},indent=2)+'\n')
    print('glyph codes',codes)
if __name__=='__main__':main()
