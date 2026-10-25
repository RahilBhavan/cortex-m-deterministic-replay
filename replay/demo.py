from trace.format import Trace

from .engine import first_divergence, replay


def main():
 t=Trace(events=[(1,2,3),(2,4,0x4000,7,1),(3,6,20,2,b"AB"),(4,8,9),(5,10,1),(6,12,0x1234),(7,14,0x55)])
 a=replay(t)
 b=replay(Trace.decode(t.encode()))
 assert first_divergence(a,b,t.events) is None
 bad=list(b)
 bad[3]=bad[3][:-1]
 d=first_divergence(a,bad,t.events)
 assert d and d["instruction"]==3
 print(
  f"demo: {len(t.encode())} bytes, {len(t.events)} event types, bit-identical model replay; "
  f"divergence at instruction {d['instruction']}"
 )
if __name__=="__main__":
    main()
