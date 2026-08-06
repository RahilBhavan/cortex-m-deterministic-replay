from .model import run
def first_divergence(a,b,events=()):
 n=min(len(a),len(b))
 for i in range(n):
  if a[i]!=b[i]:return {"instruction":i,"event_index":sum(e[1]<=i for e in events),"expected":a[i],"actual":b[i],"nearby_events":[e for e in events if abs(e[1]-i)<=2]}
 if len(a)!=len(b):return {"instruction":n,"event_index":sum(e[1]<=n for e in events),"expected":a[n] if n<len(a) else None,"actual":b[n] if n<len(b) else None,"nearby_events":[]}
 return None
def replay(trace,steps=100):return run(steps,trace.events)
