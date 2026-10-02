"""Optional artwork regeneration. Builder uses committed native palette pixels."""
import json,argparse
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('font',type=Path);a=p.parse_args()
font=ImageFont.truetype(str(a.font),14);text='NEW RELEASE!!';box=font.getbbox(text)
mask=Image.new('L',(box[2]-box[0]+2,box[3]-box[1]+2));ImageDraw.Draw(mask).text((-box[0],-box[1]),text,font=font,fill=255)
pixels=[]
for y in range(mask.height):
 row=[]
 for x in range(mask.width):
  v=mask.getpixel((x,y));shadow=mask.getpixel((x-1,y-1)) if x and y else 0
  row.append(1+round(v*14/255) if v else (3 if shadow>40 else 1))
 pixels.append(''.join(format(v,'x') for v in row))
m=dict(source='新発売!!',translation=text,meaning='newly released / newly on sale',context='Sakata EGRET AVM-12A product advertisement',font='Nimbus Sans Bold Italic 14 px',palette='existing palette 3; background index 1, white index 15',x=(224-mask.width)//2,y=128,width=mask.width,height=mask.height,pixels=pixels)
(ROOT/'data/sakata_caption.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(mask.size,m['x'])
