import argparse,json,sys
from pathlib import Path
from build_v035 import ROOT,target,raw,ptr,BASE,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('base',type=Path);p.add_argument('rom',type=Path);a=p.parse_args()
    base=a.base.read_bytes();r=a.rom.read_bytes();assert sha(base)==BASE
    template=(ROOT/'tools/controlled_template.lua').read_text()
    groups={'A':list(range(3318,3325)),'B':list(range(3340,3346)),'C':list(range(3346,3352)),'D':list(range(3352,3358))+[3227,2928]}
    for group,ids in groups.items():
        modes=['repaired','baseline']if group=='D' else ['repaired']
        for mode in modes:
            rom=base if mode=='baseline' else r
            lines=[f'local MODE="{mode}"',f'local GROUP="{group}"','local cases={']
            for j,i in enumerate(ids):
                source=955+j;old=ptr(target(rom,source));b=raw(rom,target(rom,i))
                table=3317 if 3318<=i<=3324 else 3339 if 3340<=i<=3357 else 0
                n=i-table-1 if table else 0
                nums=lambda x:'{'+','.join(map(str,x))+'}'
                lines.append(f'[{source}]={{index={i},table={table},child={n},old={nums(old)},payload={nums(b)}}},')
            lines+=['}',template];(ROOT/'qa'/f'controlled_{group}_{mode}.lua').write_text('\n'.join(lines))
if __name__=='__main__':main()
