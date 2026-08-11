import unittest
from pathlib import Path
from recorder.emulator import CortexM
from recorder.record import Recorder, decode_snapshots, encode_snapshots, record
from replay.engine import first_divergence, replay
from trace.format import Trace

ROOT = Path(__file__).resolve().parents[1]
ELF = str(ROOT / "firmware/build/race.elf")


class ReplayTest(unittest.TestCase):
    @staticmethod
    def _point_for_pc(cpu, pc):
        while cpu.pc != pc:
            cpu.step()
        return cpu.count

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

    def test_real_dma_changes_execution_and_replays(self):
        probe = CortexM(ELF)
        reset = probe.symbols["Reset_Handler"] & ~1
        point = self._point_for_pc(probe, reset + 0xC)
        address = probe.symbols["commutation"]
        payload = bytes(probe.uc.mem_read(0, 4))
        event = (3, point, address, len(payload), payload)
        trace, recorded = record(ELF, events=[event], instructions=point + 2)
        decoded = Trace.decode(trace.encode())
        replayed = replay(decoded, point + 2, elf=ELF)
        _, control = record(ELF, instructions=point + 2)
        self.assertEqual(recorded, replayed)
        self.assertNotEqual(recorded[point], control[point])
        self.assertEqual(recorded[point][2], int.from_bytes(payload, "little"))

    def test_real_replay_rejects_model_only_golden_tags(self):
        golden = Trace.decode(Path("examples/golden-demo.dtrc").read_bytes())
        build_id = CortexM(ELF).build_id
        for event in (event for event in golden.events if event[0] >= 4):
            with self.subTest(tag=event[0]), self.assertRaisesRegex(
                ValueError, "does not support event tag"
            ):
                replay(Trace(build_id, [event]), event[1] + 1, elf=ELF)

    def test_read_override_requires_matching_instruction_and_width(self):
        probe = CortexM(ELF)
        reset = probe.symbols["Reset_Handler"] & ~1
        point = self._point_for_pc(probe, reset + 0xE)
        address = probe.symbols["commutation"] + 4
        value = int.from_bytes(probe.uc.mem_read(address, 4), "little")
        with self.assertRaisesRegex(ValueError, "does not match instruction access"):
            record(ELF, events=[(2, point, address, value & 0xFF, 1)], instructions=point + 1)
        with self.assertRaisesRegex(ValueError, "does not match instruction access"):
            record(ELF, events=[(2, point - 1, address, value, 4)], instructions=point)

    def test_read_override_is_one_shot_and_preserves_backing_memory(self):
        cpu = CortexM(ELF)
        reset = cpu.symbols["Reset_Handler"] & ~1
        point = self._point_for_pc(cpu, reset + 0xE)
        address = cpu.symbols["commutation"] + 4
        original = bytes(cpu.uc.mem_read(address, 4))
        value = int.from_bytes(cpu.uc.mem_read(0, 4), "little")
        recorder = Recorder(cpu)
        recorder.event((2, point, address, value, 4))
        state = recorder.step()
        self.assertEqual(state[1], value)
        self.assertEqual(bytes(cpu.uc.mem_read(address, 4)), original)
        self.assertIsNone(cpu._read_override)


if __name__ == "__main__":
    unittest.main()
