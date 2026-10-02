from pathlib import Path
import sys
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from resources import decode,descriptor
r=Path(sys.argv[1]).read_bytes();output=Path(sys.argv[2]);output.mkdir(parents=True,exist_ok=True)
ids=[3,7,10,32,33,40,1213,1214,1224,1237,1272,1283,1284,1291,1292,1293,1294,1343,1347,1351,1407,1413,1432,1439]
for start in range(0,len(ids),6):
 sheet=Image.new('RGB',(540,570),(30,30,30));draw=ImageDraw.Draw(sheet)
 for j,i in enumerate(ids[start:start+6]):
  d=descriptor(r,i);data,end=decode(r,d['start']);assert end==d['start']+d['length']
  n=np.frombuffer(data,dtype='uint8');a=np.empty(len(n)*2,dtype='uint8');a[::2]=n>>4;a[1::2]=n&15
  tiles=a.reshape(-1,8,8);im=np.zeros(((len(tiles)+31)//32*8,256),dtype='uint8')
  for k,t in enumerate(tiles):im[k//32*8:k//32*8+8,k%32*8:k%32*8+8]=t*17
  x=8+(j%2)*270;y=8+(j//2)*190
  draw.text((x,y),f'RLE resource {i}: {len(data)} bytes / STATIC',fill='white')
  sheet.paste(Image.fromarray(im).convert('RGB'),(x,y+22))
 sheet.save(output/f'rle_sheet_{start//6}.png')
