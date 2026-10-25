import argparse
import random

from recorder.emulator import CortexM

ELF = "firmware/build/race.elf"
INJECTION_MIN = 0
INJECTION_MAX = 4


def trial(instruction_count):
    if not isinstance(instruction_count, int) or instruction_count < 0:
        raise ValueError("instruction_count must be non-negative")
    cpu = CortexM(ELF)
    for _ in range(instruction_count):
        cpu.step()
    cpu.inject_irq(0)
    for _ in range(24):
        cpu.step()
    return int.from_bytes(cpu.uc.mem_read(0x2000000c, 4), "little")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.trials <= 0:
        parser.error("--trials must be positive")
    rng = random.Random(args.seed)
    schedules = [rng.choices(range(INJECTION_MIN, INJECTION_MAX + 1), weights=(998, 1, 1, 1, 1))[0]
                 for _ in range(args.trials)]
    corruptions = sum(trial(count) for count in schedules)
    print(f"trials={args.trials} seed={args.seed} corruptions={corruptions}")


if __name__ == "__main__":
    main()
