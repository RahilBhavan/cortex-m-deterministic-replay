"""Unit tests for Thumb-16 next-PC decode and ELF symbol loading."""

from __future__ import annotations

import unittest
from pathlib import Path

from recorder.emulator import CortexM, condition_passed, thumb16_next_pc, thumb_insn_size


class ThumbDecodeTest(unittest.TestCase):
    def test_beq_taken_matches_race_elf_loop(self) -> None:
        # race.elf: 0x70 beq.n 64 when Z is set (xPSR bit 30).
        xpsr_z = 1 << 30
        self.assertEqual(thumb16_next_pc(0x70, 0xD0F8, xpsr_z), 0x64)

    def test_beq_not_taken_falls_through(self) -> None:
        self.assertEqual(thumb16_next_pc(0x70, 0xD0F8, 0), 0x72)

    def test_unconditional_b_matches_race_elf_loop(self) -> None:
        # race.elf: 0x78 b.n 64
        self.assertEqual(thumb16_next_pc(0x78, 0xE7F4, 0), 0x64)

    def test_condition_eq_uses_z_flag(self) -> None:
        self.assertTrue(condition_passed(1 << 30, 0))
        self.assertFalse(condition_passed(0, 0))

    def test_thumb_insn_size_distinguishes_32bit_prefix(self) -> None:
        self.assertEqual(thumb_insn_size(0xE7F4), 2)  # unconditional B
        self.assertEqual(thumb_insn_size(0xF04F), 4)  # mov.w first half


class SymbolDrivenLoopTest(unittest.TestCase):
    def test_reset_handler_symbols_and_branch_sites(self) -> None:
        cpu = CortexM("firmware/build/race.elf")
        # ELF Thumb symbols store the Thumb bit in the low bit of st_value.
        self.assertEqual(cpu.symbols.get("Reset_Handler", 0) & ~1, 0x58)
        self.assertEqual(cpu.symbols.get("Timer_Handler", 0) & ~1, 0x44)
        reset = cpu.symbols["Reset_Handler"] & ~1
        beq = int.from_bytes(cpu.uc.mem_read(0x70, 2), "little")
        buncond = int.from_bytes(cpu.uc.mem_read(0x78, 2), "little")
        self.assertEqual(beq, 0xD0F8)
        self.assertEqual(buncond, 0xE7F4)
        self.assertEqual(thumb16_next_pc(0x70, beq, 1 << 30), reset + 0xC)
        self.assertEqual(thumb16_next_pc(0x78, buncond, 0), reset + 0xC)

    def test_no_hardcoded_branch_addresses_in_step_path(self) -> None:
        # Guardrail: emulator source must not hardcode the old 0x70/0x78 redirects.
        source = Path("recorder/emulator.py").read_text(encoding="utf-8")
        self.assertNotIn("pc == 0x70", source)
        self.assertNotIn("pc == 0x78", source)


if __name__ == "__main__":
    unittest.main()
