import unittest
from trace.format import Trace,TraceError,readvar
from replay.engine import first_divergence
from replay.model import CPU
class TestTrace(unittest.TestCase):
 def test_all_events(self):
  e=[(1,1,2),(2,2,0x10,4,4),(3,3,20,2,b"ab"),(4,4,9),(5,5,1),(6,6,7),(7,7,8)]
  self.assertEqual(Trace.decode(Trace(events=e).encode()).events,e)
 def test_malformed(self):
  t=Trace(events=[(2,1,1,2,4)]).encode()
  for bad in (b"",t[:5],t[:-1]+b"x",t[:-4]+bytes([99])+t[-4:]):
   with self.assertRaises(TraceError):Trace.decode(bad)
 def test_encode_rejects_width_and_tags(self):
  for event in ((2,1,1,2,3),(256,1,0),(-1,1,0),(99,1,0),("irq",1,0)):
   with self.assertRaises(TraceError):Trace(events=[event]).encode()
 def test_varint_rejects_unsigned_64_bit_overflow(self):
  with self.assertRaises(TraceError):readvar(bytes([128]) * 9 + bytes([2]),0)
 def test_length_diff(self):
  d=first_divergence([("a",)],[],[]);self.assertEqual(d["instruction"],0)
 def test_dma_rejects_memory_overrun(self):
  c=CPU()
  with self.assertRaises(TraceError):c.apply((3,0,255,2,b"ab"))
  self.assertEqual(len(c.mem),256)
if __name__=="__main__":unittest.main()
