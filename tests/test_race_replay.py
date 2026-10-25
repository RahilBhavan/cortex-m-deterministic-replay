import random
import unittest
from pathlib import Path

from recorder.emulator import CortexM
from recorder.race_rate import trial
from recorder.record import Recorder
from replay.engine import replay
from tests.firmware import requires_firmware

ROOT = Path(__file__).resolve().parents[1]
ELF = str(ROOT / "firmware/build/race.elf")


class RaceReplayTest(unittest.TestCase):
    @requires_firmware
    def test_same_point_events_use_canonical_order_before_recording(self):
        probe = CortexM(ELF)
        vector_address = 4 * 16
        default_vector = (probe.symbols["Default_Handler"] | 1).to_bytes(4, "little")
        cpu = CortexM(ELF)
        recorder = Recorder(cpu)
        recorder.event((3, 0, vector_address, len(default_vector), default_vector))
        recorder.event((1, 0, 0))
        recorded = recorder.run(8)
        trace = recorder.trace()
        self.assertEqual([event[0] for event in trace.events], [1, 3])
        self.assertEqual(recorded, replay(trace, 8, elf=ELF))
        self.assertEqual(recorded[0][15], (probe.symbols["Timer_Handler"] & ~1) + 2)

    @requires_firmware
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
