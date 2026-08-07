"""Record deterministic external events and complete CPU snapshots."""
import argparse
import struct
from trace.format import Trace
from .emulator import CortexM

INSTRUCTIONS = 100_000
SNAPSHOT_WORDS = 17


def encode_snapshots(states):
    encoded = bytearray()
    for state in states:
        if len(state) != SNAPSHOT_WORDS:
            raise ValueError("snapshot must contain 17 fields")
        encoded += struct.pack("<17I", *state)
    return bytes(encoded)


def decode_snapshots(data):
    if not isinstance(data, (bytes, bytearray)) or len(data) % (SNAPSHOT_WORDS * 4):
        raise ValueError("truncated snapshot stream")
    return [struct.unpack_from("<17I", data, offset)
            for offset in range(0, len(data), SNAPSHOT_WORDS * 4)]


class Recorder:
    def __init__(self, cpu):
        self.cpu = cpu
        self.states = []
        self.events = []

    def event(self, event):
        self.events.append(tuple(event))

    def step(self):
        point = self.cpu.count
        for event in self.events:
            if event[1] != point:
                continue
            if event[0] == 1:
                self.cpu.inject_irq(event[2])
            elif event[0] == 2:
                self.cpu.mmio[event[2]] = event[3]
            elif event[0] == 3:
                self.cpu.dma(event[2], event[4])
        state = self.cpu.step()
        self.states.append(state)
        return state

    def run(self, count=INSTRUCTIONS):
        if count < 0:
            raise ValueError("instruction count must be non-negative")
        while len(self.states) < count:
            self.step()
        return self.states

    def trace(self):
        return Trace(self.cpu.build_id, sorted(self.events, key=lambda e: (e[1], e[0])))


def record(elf, events=(), instructions=INSTRUCTIONS):
    recorder = Recorder(CortexM(elf))
    for event in events:
        recorder.event(event)
    recorder.run(instructions)
    return recorder.trace(), recorder.states


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("elf")
    parser.add_argument("--count", type=int, default=INSTRUCTIONS)
    args = parser.parse_args()
    trace, states = record(args.elf, instructions=args.count)
    print(f"recorded {len(states)}/{args.count} build={trace.build_id.hex()}")


if __name__ == "__main__":
    main()
