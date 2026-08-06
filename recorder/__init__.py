from trace.format import Trace
def record(events,build_id=b"demo-v1"): return Trace(build_id,events)
