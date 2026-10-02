from pathlib import Path
import sys
from PIL import Image
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from resources import descriptor,decode
def screen(w):
 out=np.zeros((144,224,3),dtype='uint8')
 pal=[]
 for p in range(256):
  v=int.from_bytes(w[0xfe00+2*p:0xfe02+2*p],'little');pal.append(((v>>8&15)*17,(v>>4&15)*17,(v&15)*17))
 for y in range(18):
  for x in range(28):
   a=0x2800+y*64+x*2;v=int.from_bytes(w[a:a+2],'little');t=v&511;pl=(v>>9)&15
   p=0x4000+t*32+(0x4000 if v&0x2000 else 0)
   b=np.frombuffer(w[p:p+32],dtype='uint8');a=np.empty(64,dtype='uint8');a[::2]=b>>4;a[1::2]=b&15;a=a.reshape(8,8)
   if v&0x4000:a=a[:,::-1]
   if v&0x8000:a=a[::-1]
   out[y*8:y*8+8,x*8:x*8+8]=np.array(pal[pl*16:pl*16+16],dtype='uint8')[a]
 return Image.fromarray(out)
if __name__=='__main__':
 r=Path(sys.argv[1]).read_bytes();w=bytearray(Path(sys.argv[2]).read_bytes());output=Path(sys.argv[3]);output.mkdir(parents=True,exist_ok=True)
 for i in range(13,23):
  d=descriptor(r,i);data,end=decode(r,d['start']);w[0x6600:0x8000]=data
  screen(w).save(output/f'ad_{i}_STATIC.png')
