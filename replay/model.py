from trace.format import TraceError

class CPU:
 def __init__(self):self.r=[0]*13;self.sp=0x20000000;self.lr=0;self.pc=0;self.xpsr=0x01000000;self.mem=bytearray(256);self.count=0;self.external=0;self.race=0
 def apply(self,e):
  k=e[0]
  if k==1:self.r[12]=(self.r[12]+e[2])&0xffffffff
  elif k==2:self.r[0]=e[3]
  elif k==3:
   if e[2]<0 or e[2]+len(e[4])>len(self.mem):raise TraceError("DMA span out of range")
   self.mem[e[2]:e[2]+len(e[4])]=e[4]
  elif k==4:self.external=e[2]
  elif k==5:self.race=e[2]
  elif k==6:self.mem[:4]=e[2].to_bytes(4,"little")
  elif k==7:self.r[11]=e[2]
 def step(self):self.r[1]=(self.r[1]+self.race+self.external+self.mem[self.count%256])&0xffffffff;self.pc=(self.pc+2)&0xffffffff;self.count+=1
 def state(self):return tuple(self.r)+(self.sp,self.lr,self.pc,self.xpsr)+tuple(self.mem)
def run(steps=100,events=()):
 c=CPU();by={}
 for e in events:by.setdefault(e[1],[]).append(e)
 out=[]
 for _ in range(steps):
  for e in by.get(c.count,[]):c.apply(e)
  c.step();out.append(c.state())
 return out
