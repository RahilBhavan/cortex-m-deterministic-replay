"""Shared skip guard for tests that execute the built firmware image."""
import unittest
from pathlib import Path

ELF = Path(__file__).resolve().parents[1] / "firmware" / "build" / "race.elf"

requires_firmware = unittest.skipUnless(
    ELF.is_file(), "firmware/build/race.elf is missing: run `make firmware` (needs arm-none-eabi-gcc)"
)
