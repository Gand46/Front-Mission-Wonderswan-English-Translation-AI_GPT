from pathlib import Path
import struct,json
def decode(r,p,limit=65536):
 out=bytearray();start=p
 while len(out)<=limit and p-start<65536:
  b=r[p];p+=1
  if b==0xee:return bytes(out),p
  if b==0x77:out.append(r[p]);p+=1
  elif b in (0xbb,0xcc,0xdd):
   n=r[p];p+=1
   v=0 if b==0xbb else 255
   if b==0xdd:v=r[p];p+=1
   out.extend([v]*n)
  elif b in (0x88,0x99,0xaa):
   n=2
   if b!=0x99:n=r[p];p+=1
   v=int.from_bytes(r[p:p+2],'little');p+=2
   if b==0xaa:
    if n==0:n=65536
    for k in range(n):out.extend(((v+k)&65535).to_bytes(2,'little'))
   else:out.extend(v.to_bytes(2,'little')*n)
  else:out.append(b)
 raise ValueError('Decode limit')
def descriptor(r,i,table=0x749b90):
 p=table+i*6;o,b,n=struct.unpack_from('<HHH',r,p)
 return dict(index=i,descriptor=hex(p),start=(b&127)*65536+o,bank=b,length=n)
def encode(data):
 """Optimal bounded RLE, matching the game decoder at 4000:6E86."""
 n=len(data);cost=[10**9]*(n+1);choice=[None]*n;cost[n]=1
 specials={0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee}
 for i in range(n-1,-1,-1):
  v=data[i];literal=bytes((0x77,v)) if v in specials else bytes((v,))
  cost[i]=len(literal)+cost[i+1];choice[i]=(1,literal)
  def offer(k,b):
   c=len(b)+cost[i+k]
   if c<cost[i]:cost[i]=c;choice[i]=(k,b)
  run=1
  while run<255 and i+run<n and data[i+run]==v:run+=1
  for k in range(2,run+1):offer(k,bytes((0xbb if v==0 else 0xcc,k)) if v in (0,255) else bytes((0xdd,k,v)))
  if i+3<n:
   w=data[i:i+2];j=1
   while j<255 and i+2*j+2<=n and data[i+2*j:i+2*j+2]==w:j+=1
   for k in range(2,j+1):offer(2*k,b'\x99'+w if k==2 else bytes((0x88,k))+w)
   v2=int.from_bytes(w,'little');j=1
   while j<255 and i+2*j+2<=n and int.from_bytes(data[i+2*j:i+2*j+2],'little')==(v2+j)&65535:j+=1
   for k in range(2,j+1):offer(2*k,bytes((0xaa,k))+w)
 out=bytearray();i=0
 while i<n:k,b=choice[i];out+=b;i+=k
 return bytes(out)+b'\xee'
