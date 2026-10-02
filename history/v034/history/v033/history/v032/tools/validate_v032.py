#!/usr/bin/env python3
"""Static audit, patch round-trips, editable binary-derived corpus and previews."""
import argparse, json
from collections import Counter
from pathlib import Path
from build_v032 import ROOT,CLEAN,V31,sha,build,make_ips,apply_ips,target,label_pixels,decode_pixels
from audit_japanese import parse,JP_LABEL_CODES

def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--clean',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--previews',action='store_true');a=p.parse_args()
    clean=a.clean.read_bytes();r=a.rom.read_bytes()
    if sha(clean)!=CLEAN:raise SystemExit('Wrong clean ROM')
    v31=apply_ips(clean,(ROOT/'patches/baseline_v031_from_clean.ips').read_bytes())
    assert sha(v31)==V31
    m=json.loads((ROOT/'data/translations_v032.json').read_text(encoding='utf-8'))
    expected,report=build(v31,m);assert r==expected
    assert len(r)==8388608 and sum(r[:-2])&65535==int.from_bytes(r[-2:],'little')
    table={bytes.fromhex(x['code'].replace(':','')):x['unicode'] for x in json.loads((ROOT/'data/wsc_unicode_table_v0.13.json').read_text(encoding='utf-8'))['entries']}
    # Classification uses NEW glyph art, not the legacy Unicode values alone.
    localized={x['code']:x['label'] for x in m['labels']}
    table.update({bytes.fromhex(k.replace(':','')):'['+v+']' for k,v in localized.items()})
    rows=[];jp=[];unknown=[];attribute_entries=[]
    for i in range(3358):
        offset=target(r,i)
        if i in (3317,3339):
            n=7 if i==3317 else 18
            rows.append({'index':i,'target':hex(offset),'category':'NESTED_TABLE_UNRESOLVED','hex':r[offset:offset+2*n+2].hex(' ')})
            assert r[offset:offset+2*n+2]==v31[offset:offset+2*n+2]
            continue
        rec=parse(r,offset,table);old=parse(v31,target(v31,i),table)
        assert rec['terminated'],i
        assert offset//65536==(int(rec['end'],16)-1)//65536,i
        cat='NAME_ENTRY_GRID_PRESERVED' if 709<=i<=939 else 'TEXT_OR_CONTROL'
        if cat=='NAME_ENTRY_GRID_PRESERVED':assert rec['hex']==old['hex'] and offset==target(v31,i)
        else:
            if rec['japanese']:jp.append(i)
            if set(rec['unknown'])-{'C0:2F','C6:45','C6:49','C6:4F'}:unknown.append(i)
            if any(u[2].upper() in {x.replace(':','') for x in localized} for u in rec['units']):attribute_entries.append(i)
        if i not in {1011,*range(2099,2104)}:assert rec['hex']==old['hex'] and offset==target(v31,i)
        rows.append({'index':i,'target':hex(offset),'category':cat,**{k:v for k,v in rec.items() if k!='units'}})
    assert not jp and not unknown,(jp,unknown)
    assert len(attribute_entries)==464
    assert len({target(r,i) for i in attribute_entries})==463
    assert all(rows[i]['text']=='{FC:01}:{BR}test{END}' for i in range(2099,2104))
    assert rows[1011]['text']==m['bank_boundary_fix']['translation']+'{END}'
    for x in m['labels']:
        a2=decode_pixels(label_pixels(x['label']))
        assert all(v==6 for row in a2 for v in row[8:]),x
    delta=make_ips(v31,r);cumulative=make_ips(clean,r)
    assert apply_ips(v31,delta)==r and apply_ips(clean,cumulative)==r
    (ROOT/'patches/v032_TEST_from_v031.ips').write_bytes(delta)
    (ROOT/'patches/v032_TEST_from_clean.ips').write_bytes(cumulative)
    dump(ROOT/'data/binary_derived_corpus_v032.json',{'provenance':'Decoded from patched binary; not the missing canonical v0.26+ editorial manifest. Hex bytes are authoritative; bracketed labels denote single glyphs. Two arrays are data, not text.','entries':rows})
    summary={'version':'v0.32-TEST','rom_sha256':sha(r),'checksum':report['checksum'],'static_status':'PASS','runtime_status':'BLOCKED_NO_X_SERVER','main_entries':3358,'translated_attribute_glyphs':16,'affected_attribute_entries':464,'affected_attribute_unique_targets':463,'translated_test_slots':5,'test_runtime_use':'UNPROVEN','remaining_japanese_in_audited_main_text_excluding_grid_and_nested_arrays':jp,'unclassified_glyph_entries_in_same_scope':unknown,'preserved_name_grid_entries':231,'unresolved_nested_tables':[3317,3339],'unresolved_nested_children':25,'whole_game_translation_complete':False,'patch_roundtrips':'PASS','change_whitelist':'PASS','all_non_test_main_text_bytes_unchanged':'PASS','font_engine_unchanged':True,'changed_bytes':report['changed_bytes'],'cumulative_patch_sha256':sha(cumulative),'delta_patch_sha256':sha(delta),'disclaimer':'Zero applies ONLY to the decoded main-table scope; does not certify graphics, special FD glyphs, secondary tables, name-entry glyphs, or every runtime path.'}
    summary['all_non_changed_main_text_bytes_unchanged']=summary.pop('all_non_test_main_text_bytes_unchanged')
    summary['bank_boundary_fix']={'index':1011,'previous_target':'0x7BFFFB','new_target':'0x7C0000','status':'PASS_STATIC','remaining_cross_bank_records':0}
    dump(ROOT/'evidence/static_validation.json',summary)
    if a.previews:
        from PIL import Image,ImageDraw
        from render_evidence import glyph_image
        atlas=Image.new('RGB',(840,70+16*72),(18,24,34));d=ImageDraw.Draw(atlas)
        d.text((15,15),'v0.31 -> v0.32-TEST | direct ROM pixels, 3x nearest-neighbor',fill='white')
        d.text((15,34),'STATIC ART ONLY. Not emulator screenshots or a runtime layout certification.',fill='yellow')
        for j,x in enumerate(m['labels']):
            y=65+j*72;gid=7*192+int(x['code'].split(':')[1],16)
            d.text((15,y+12),x['code'],fill='white')
            atlas.paste(glyph_image(v31,gid).resize((48,48),Image.Resampling.NEAREST),(90,y))
            atlas.paste(glyph_image(r,gid).resize((48,48),Image.Resampling.NEAREST),(170,y))
            d.text((235,y+12),x['label']+'  '+x['meaning'],fill='white')
        atlas.save(ROOT/'evidence/attribute_glyphs_before_after_STATIC.png')
        preview=Image.new('RGB',(920,650),(18,24,34));d=ImageDraw.Draw(preview)
        d.text((15,12),'STATIC simulated 8/4 px cadence. FC/FD rendering omitted; NOT gameplay.',fill='yellow')
        for j,i in enumerate((137,138,139,496,545,2099)):
            strip=Image.new('RGB',(224,48),(18,24,34));x=0;y=0
            for pos,kind,raw,g,label in parse(r,target(r,i),table)['units']:
                if raw in ('fa','fe'):x=0;y+=16
                if kind=='glyph':
                    im=glyph_image(r,g)
                    # Transparent backgrounds prevent erasing the previous glyph's ink.
                    for yy in range(16):
                        for xx in range(16):
                            c=im.getpixel((xx,yy))
                            if c!=(18,24,34) and x+xx<224 and y+yy<48:strip.putpixel((x+xx,y+yy),c)
                    x+=4 if len(raw)==2 and 0xBB<=int(raw,16)<=0xBF else 8
            preview.paste(strip.resize((672,144),Image.Resampling.NEAREST).crop((0,0,672,96)),(190,45+j*100))
            d.text((15,60+j*100),'Entry '+str(i),fill='white')
        preview.save(ROOT/'evidence/attribute_samples_STATIC.png')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
