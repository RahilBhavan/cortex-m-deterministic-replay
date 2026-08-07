import unittest
from pathlib import Path
from recorder.record import decode_snapshots, encode_snapshots, record
from replay.engine import first_divergence, replay

ROOT = Path(__file__).resolve().parents[1]
ELF = str(ROOT / "firmware/build/race.elf")


class ReplayTest(unittest.TestCase):
    def test_real_100000_snapshot_replay(self):
        trace, recorded = record(ELF, instructions=100000)
        replayed = replay(trace, 100000, elf=ELF)
        self.assertEqual(len(recorded), 100000)
        self.assertTrue(all(len(state) == 17 for state in recorded))
        self.assertTrue(all(len(state) == 17 for state in replayed))
        self.assertIsNone(first_divergence(recorded, replayed, trace.events))
        self.assertEqual(decode_snapshots(encode_snapshots(recorded)), recorded)

    def test_build_id_is_required(self):
        trace, _ = record(ELF, instructions=1)
        trace.build_id = b"wrong-build"
        with self.assertRaises(ValueError):
            replay(trace, 1, elf=ELF)


if __name__ == "__main__":
    unittest.main()
