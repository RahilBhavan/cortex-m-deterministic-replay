"""Explain the first state difference between two replay streams."""
import argparse
import subprocess
from replay.engine import first_divergence


def disassembly(pc, elf=None):
    if pc is None or not elf:
        return None
    try:
        result = subprocess.run(
            ["arm-none-eabi-objdump", "-d", f"--start-address={pc:#x}",
             f"--stop-address={pc + 4:#x}", elf], capture_output=True,
            text=True, check=True)
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def compare(expected, actual, events=(), elf=None):
    result = first_divergence(expected, actual, events)
    if result and result["expected"] is not None:
        result["expected_pc"] = result["expected"][15]
        result["actual_pc"] = (result["actual"][15]
                                if result["actual"] is not None else None)
        result["disassembly"] = disassembly(result["expected_pc"], elf)
        result["actual_disassembly"] = disassembly(result["actual_pc"], elf)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf")
    args = parser.parse_args()
    print(compare([], [], elf=args.elf))


if __name__ == "__main__":
    main()
