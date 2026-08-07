import subprocess
import sys
import unittest
from recorder.emulator import CortexM
from recorder.race_rate import trial


class FirmwareRaceTest(unittest.TestCase):
    def test_irq_enters_and_returns(self):
        cpu = CortexM("firmware/build/race.elf")
        for _ in range(6):
            cpu.step()
        pc = cpu.pc
        cpu.inject_irq(0)
        self.assertEqual(cpu.pc, 0x44)
        for _ in range(7):
            cpu.step()
        self.assertEqual(cpu.pc, pc)

    def test_multiple_insertion_points(self):
        self.assertEqual(trial(3), 1)
        self.assertEqual(trial(4), 1)
        self.assertEqual(trial(0), 0)
        self.assertEqual(trial(1), 0)
        self.assertEqual(trial(2), 0)

    def test_schedule_reproducible(self):
        cmd = [sys.executable, "-m", "recorder.race_rate", "--trials", "1000", "--seed", "0"]
        first = subprocess.check_output(cmd, text=True)
        self.assertEqual(first, subprocess.check_output(cmd, text=True))
        self.assertEqual(first, "trials=1000 seed=0 corruptions=2\n")

    def test_seed0_campaign_locks_two_corruptions(self):
        """Lock the resume/verification claim: seed 0 yields exactly two corruptions."""
        out = subprocess.check_output(
            [sys.executable, "-m", "recorder.race_rate", "--trials", "1000", "--seed", "0"],
            text=True,
        )
        self.assertEqual(out.strip(), "trials=1000 seed=0 corruptions=2")

    def test_rejects_nonpositive_trials(self):
        result = subprocess.run(
            [sys.executable, "-m", "recorder.race_rate", "--trials", "0"],
            capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
