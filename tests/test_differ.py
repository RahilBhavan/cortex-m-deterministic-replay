import unittest
from pathlib import Path
from recorder.record import record
from replay.engine import replay
from tools.differ import compare
from trace.format import Trace

ROOT = Path(__file__).resolve().parents[1]
ELF = str(ROOT / "firmware/build/race.elf")


class DifferTest(unittest.TestCase):
    def test_altered_mmio_reports_first_difference(self):
        event = (2, 5, 0x20000004, 1, 4)
        trace, expected = record(ELF, events=[(2, 5, 0x20000004, 0, 4)], instructions=20)
        actual = replay(Trace(trace.build_id, [event]), 20, elf=ELF)
        result = compare(expected, actual, trace.events, ELF)
        self.assertIsNotNone(result)
        self.assertEqual(result["instruction"], 6)
        self.assertIn("Disassembly", result["disassembly"])
        self.assertEqual(result["nearby_events"], [trace.events[0]])

    def test_missing_actual_state_has_no_disassembly(self):
        result = compare([(0,) * 17], [], elf=ELF)
        self.assertIsNone(result["actual_pc"])
        self.assertIsNone(result["actual_disassembly"])


if __name__ == "__main__":
    unittest.main()
