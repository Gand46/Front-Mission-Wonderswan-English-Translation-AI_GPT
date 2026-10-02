"""Synthetic QA only; never package this ROM as the translation."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_v033 import sha
sys.path.insert(0,str(ROOT/'history/v032/tools'))
from build_v032 import ONE,target
cases={983:'Alpha beta gamma delta epsilon zeta eta theta iota kappa.',
       984:'abcdefghijklmnopqrstuv W',
       955:'Alpha beta gamma delta epsilon zeta eta theta iota kappa.'}
def main():
 r=bytearray(Path(sys.argv[1]).read_bytes());before=sha(r)
 corpus=json.loads((ROOT/'history/v032/data/binary_derived_corpus_v032.json').read_text())['entries']
 for i,t in cases.items():
  b=b''.join(bytes((0xc0,0x40+ord(c)-65)) if c.isupper() else bytes((ONE[c],)) for c in t)+b'\xff'
  p=target(r,i);assert len(b)<=corpus[i]['length']
  r[p:p+len(b)]=b
 r[-2:]=(sum(r[:-2])&65535).to_bytes(2,'little')
 out=Path(sys.argv[2]);assert not out.exists();out.write_bytes(r)
 print(json.dumps(dict(synthetic_only=True,base_sha256=before,qa_rom_sha256=sha(r),cases=cases),indent=2))
if __name__=='__main__':main()
