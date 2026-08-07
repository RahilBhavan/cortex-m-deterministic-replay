"""Race-first Phase-0 demo: seed-0 campaign plus one corrupting schedule replay."""

from __future__ import annotations

import random
import sys
from pathlib import Path

from recorder.emulator import CortexM
from recorder.race_rate import trial
from recorder.record import Recorder
from replay.engine import replay

ROOT = Path(__file__).resolve().parents[1]
ELF = str(ROOT / "firmware/build/race.elf")
EXPECTED_SEED0_CORRUPTIONS = 2
TRIALS = 1000
SEED = 0


def _seed0_corruptions() -> int:
    """Run the documented seed-0 campaign and return the corruption count."""
    rng = random.Random(SEED)
    schedules = [
        rng.choices(range(5), weights=(998, 1, 1, 1, 1))[0] for _ in range(TRIALS)
    ]
    return sum(trial(count) for count in schedules)


def _first_corrupting_count() -> int:
    """Return the first insertion count from seed 0 that corrupts the invariant."""
    rng = random.Random(SEED)
    schedules = [
        rng.choices(range(5), weights=(998, 1, 1, 1, 1))[0] for _ in range(TRIALS)
    ]
    return next(count for count in schedules if trial(count))


def _replay_corrupting_schedule(count: int) -> None:
    """Record and replay one corrupting schedule; require identical 17-field snapshots."""
    cpu = CortexM(ELF)
    recorder = Recorder(cpu)
    for _ in range(count):
        recorder.step()
    recorder.event((1, cpu.count, 0))
    recorded = recorder.run(24)
    replayed = replay(recorder.trace(), 24, elf=ELF)
    if recorded != replayed:
        raise AssertionError("recorded and replayed snapshots diverge")
    corruptions = int.from_bytes(cpu.uc.mem_read(0x2000000C, 4), "little")
    if corruptions != 1:
        raise AssertionError(f"expected corruption flag 1, got {corruptions}")


def main() -> int:
    """Print the race demo summary used by `make demo`."""
    if not Path(ELF).is_file():
        print(f"demo blocked: missing {ELF}; run `make firmware` first", file=sys.stderr)
        return 1
    corruptions = _seed0_corruptions()
    print(f"trials={TRIALS} seed={SEED} corruptions={corruptions}")
    if corruptions != EXPECTED_SEED0_CORRUPTIONS:
        print(
            f"demo failed: expected corruptions={EXPECTED_SEED0_CORRUPTIONS}",
            file=sys.stderr,
        )
        return 1
    count = _first_corrupting_count()
    _replay_corrupting_schedule(count)
    print(
        f"corrupting schedule count={count}: Unicorn record/replay identity ok "
        f"(corruption flag set)"
    )
    print("demo: race seed 0 locked; one corrupting schedule replayed bit-identically")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
