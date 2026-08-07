import random
import unittest
from pathlib import Path
from recorder.emulator import CortexM
from recorder.record import Recorder
from recorder.race_rate import trial
from replay.engine import replay

ROOT = Path(__file__).resolve().parents[1]
ELF = str(ROOT / "firmware/build/race.elf")


class RaceReplayTest(unittest.TestCase):
    def test_corrupting_seed_schedule_replays_20_of_20(self):
        rng = random.Random(0)
        schedules = [rng.choices(range(5), weights=(998, 1, 1, 1, 1))[0]
                     for _ in range(1000)]
        count = next(count for count in schedules if trial(count))
        self.assertEqual(trial(0), 0)
        self.assertEqual(trial(count), 1)
        for _ in range(20):
            cpu = CortexM(ELF)
            recorder = Recorder(cpu)
            for _ in range(count):
                recorder.step()
            recorder.event((1, cpu.count, 0))
            recorded = recorder.run(24)
            replayed = replay(recorder.trace(), 24, elf=ELF)
            self.assertEqual(recorded, replayed)
            self.assertEqual(int.from_bytes(cpu.uc.mem_read(0x2000000c, 4), "little"), 1)


if __name__ == "__main__":
    unittest.main()
