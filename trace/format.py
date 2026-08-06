"""Validated compact trace contract."""
import struct,zlib
MAGIC=b"DTRC"; VERSION=2
class TraceError(ValueError): pass
def varint(n):
 if not isinstance(n,int) or n<0: raise TraceError("invalid integer")
 o=b""
 while n>127:o+=bytes([(n&127)|128]);n>>=7
 return o+bytes([n])
def readvar(b,i):
 n=s=0
 while i<len(b):
  x=b[i];i+=1
  if s==63 and x>1:raise TraceError("varint overflow")
  n|=(x&127)<<s
  if x<128:return n,i
  s+=7
  if s>63:raise TraceError("varint overflow")
 raise TraceError("truncated varint")
class Trace:
 def __init__(self,build_id=b"demo-v1",events=()):
  if not isinstance(build_id,(bytes,bytearray)) or not build_id or len(build_id)>255:raise TraceError("invalid build id")
  self.build_id=bytes(build_id);self.events=list(events)
 def encode(self):
  out=bytearray(MAGIC+bytes([VERSION,len(self.build_id)])+self.build_id);last=0
  for e in self.events:
   if not isinstance(e,tuple) or len(e)<2 or not isinstance(e[1],int) or e[1]<last:raise TraceError("bad event point")
   k,n=e[:2]
   if not isinstance(k,int) or k not in range(1,8):raise TraceError("unknown event")
   out+=bytes([k])+varint(n-last);last=n
   try:
    if k==1: out+=struct.pack("<B",e[2])
    elif k==2:
     if e[4] not in (1,2,4):raise TraceError("invalid width")
     out+=struct.pack("<IIB",e[2],e[3],e[4])
    elif k==3:
     p=e[4];
     if not isinstance(p,bytes) or len(p)>65535 or e[3]>65535:raise TraceError("bad dma payload")
     out+=struct.pack("<IIH",e[2],e[3],len(p))+p
    elif k==4: out+=struct.pack("<I",e[2])
    elif k==5: out+=struct.pack("<B",e[2])
    elif k==6: out+=struct.pack("<I",e[2])
    elif k==7: out+=struct.pack("<I",e[2])
    else: raise TraceError("unknown event")
   except (IndexError,TypeError,ValueError,struct.error):raise TraceError("malformed event")
  return bytes(out)+struct.pack("<I",zlib.crc32(out))
 @classmethod
 def decode(cls,b):
  if not isinstance(b,(bytes,bytearray)) or len(b)<10 or b[:4]!=MAGIC or b[4]!=VERSION:raise TraceError("bad header")
  n=b[5];end=6+n
  if not n or len(b)<end+4:raise TraceError("truncated header")
  body=b[:-4]
  if struct.unpack("<I",b[-4:])[0]!=zlib.crc32(body):raise TraceError("checksum mismatch")
  i=end;last=0;es=[]
  while i<len(body):
   k=body[i];i+=1;d,i=readvar(body,i);pc=last+d
   if pc<last:raise TraceError("nonmonotonic point")
   last=pc
   try:
    if k==1: es.append((k,pc,body[i]));i+=1
    elif k==2:
     a,v,w=struct.unpack_from("<IIB",body,i);i+=9
     if w not in (1,2,4):raise TraceError("invalid width")
     es.append((k,pc,a,v,w))
    elif k==3:
     a,l,z=struct.unpack_from("<IIH",body,i);i+=10
     if z!=l or i+z>len(body):raise TraceError("DMA length mismatch")
     es.append((k,pc,a,l,body[i:i+z]));i+=z
    elif k in (4,6,7):v=struct.unpack_from("<I",body,i)[0];i+=4;es.append((k,pc,v))
    elif k==5:es.append((k,pc,body[i]));i+=1
    else:raise TraceError("unknown event")
   except (IndexError,struct.error):raise TraceError("truncated event")
  if i!=len(body):raise TraceError("trailing data")
  return cls(body[6:6+n],es)
