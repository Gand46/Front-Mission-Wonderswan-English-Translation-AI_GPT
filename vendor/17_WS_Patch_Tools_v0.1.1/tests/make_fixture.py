#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1]); root.mkdir(parents=True,exist_ok=True)
s=bytearray((i*37)&255 for i in range(8192)); t=bytearray(s)
t[100:140]=b'A'*40; t[1000:1020]=bytes(range(20)); t.extend(b'EXTRA-DATA')
(root/'source.bin').write_bytes(s); (root/'target.bin').write_bytes(t)
