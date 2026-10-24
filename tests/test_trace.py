import random
import unittest
from pathlib import Path
from trace.format import Trace, TraceError, readvar

from replay.engine import first_divergence
from replay.model import CPU


class TestTrace(unittest.TestCase):
 def test_all_events(self):
  e=[(1,1,2),(2,2,0x10,4,4),(3,3,20,2,b"ab"),(4,4,9),(5,5,1),(6,6,7),(7,7,8)]
  self.assertEqual(Trace.decode(Trace(events=e).encode()).events,e)
 def test_malformed(self):
  t=Trace(events=[(2,1,1,2,4)]).encode()
  for bad in (b"",t[:5],t[:-1]+b"x",t + b"trailing",t[:-4]+bytes([99])+t[-4:]):
   with self.assertRaises(TraceError):
       Trace.decode(bad)

 def test_10000_deterministic_random_round_trips(self):
  rng=random.Random(0xD7AC)
  for _ in range(10000):
   point=rng.randrange(1 << 20)
   kind=rng.randrange(1, 8)
   if kind == 1:
       event=(kind,point,rng.randrange(256))
   elif kind == 2:
    width=rng.choice((1,2,4))
    event=(kind,point,rng.randrange(1 << 32),rng.randrange(1 << (8*width)),width)
   elif kind == 3:
    payload=bytes(rng.randrange(256) for _ in range(rng.randrange(8)))
    event=(kind,point,rng.randrange(1 << (32-len(payload))),len(payload),payload)
   elif kind == 5:
       event=(kind,point,rng.randrange(256))
   else:
       event=(kind,point,rng.randrange(1 << 32))
   self.assertEqual(Trace.decode(Trace(events=[event]).encode()).events,[event])

 def test_bounds_and_canonical_same_count(self):
  with self.assertRaises(TraceError):
      Trace(build_id=b"x" * 65)
  with self.assertRaises(TraceError):
      Trace(events=[(2,1,0,0,4),(1,1,0)]).encode()
  with self.assertRaises(TraceError):
      Trace(events=[(3,1,0,2,b"x")]).encode()
  with self.assertRaises(TraceError):
      Trace(events=[(2,1,0,256,1)]).encode()
 def test_encode_rejects_width_and_tags(self):
  for event in ((2,1,1,2,3),(256,1,0),(-1,1,0),(99,1,0),("irq",1,0)):
   with self.assertRaises(TraceError):
       Trace(events=[event]).encode()
 def test_varint_rejects_unsigned_64_bit_overflow(self):
  with self.assertRaises(TraceError):
      readvar(bytes([128]) * 9 + bytes([2]),0)
 def test_varint_rejects_nonminimal_encoding(self):
  with self.assertRaises(TraceError):
      readvar(bytes([128, 0]), 0)
 def test_length_diff(self):
  d=first_divergence([("a",)],[],[])
  self.assertEqual(d["instruction"],0)
 def test_dma_rejects_memory_overrun(self):
  c=CPU()
  with self.assertRaises(TraceError):
      c.apply((3,0,255,2,b"ab"))
  self.assertEqual(len(c.mem),256)
 def test_checked_in_golden_bytearray_round_trip(self):
  data=Path("examples/golden-demo.dtrc").read_bytes()
  decoded=Trace.decode(bytearray(data))
  self.assertIsInstance(decoded.events[2][4],bytes)
  self.assertEqual(decoded.encode(),data)
  self.assertEqual(bytes.fromhex(Path("examples/golden-demo.hex").read_text()),data)
 def test_rejects_extra_event_fields(self):
  events=[(1,0,1,99),(2,0,0,0,4,99),(3,0,0,0,b"",99),
          (4,0,1,99),(5,0,1,99),(6,0,1,99),(7,0,1,99)]
  for event in events:
   with self.subTest(event=event),self.assertRaises(TraceError):
    Trace(events=[event]).encode()
if __name__=="__main__":
    unittest.main()
