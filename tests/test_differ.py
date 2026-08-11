import unittest
from pathlib import Path
from recorder.record import record
from recorder.emulator import CortexM
from replay.engine import replay
from tools.differ import compare
from trace.format import Trace

ROOT = Path(__file__).resolve().parents[1]
ELF = str(ROOT / "firmware/build/race.elf")


class DifferTest(unittest.TestCase):
    def test_altered_read_override_reports_first_difference(self):
        probe = CortexM(ELF)
        reset = probe.symbols["Reset_Handler"] & ~1
        while probe.pc != reset + 0xE:
            probe.step()
        point = probe.count
        address = probe.symbols["commutation"] + 4
        expected_value = int.from_bytes(probe.uc.mem_read(probe.symbols["commutation"], 4), "little")
        actual_value = int.from_bytes(probe.uc.mem_read(0, 4), "little")
        event = (2, point, address, actual_value, 4)
        trace, expected = record(
            ELF, events=[(2, point, address, expected_value, 4)], instructions=20
        )
        actual = replay(Trace(trace.build_id, [event]), 20, elf=ELF)
        result = compare(expected, actual, trace.events, ELF)
        self.assertIsNotNone(result)
        self.assertEqual(result["instruction"], point)
        self.assertIn("Disassembly", result["disassembly"])
        self.assertEqual(result["nearby_events"], [trace.events[0]])

    def test_missing_actual_state_has_no_disassembly(self):
        result = compare([(0,) * 17], [], elf=ELF)
        self.assertIsNone(result["actual_pc"])
        self.assertIsNone(result["actual_disassembly"])


if __name__ == "__main__":
    unittest.main()
