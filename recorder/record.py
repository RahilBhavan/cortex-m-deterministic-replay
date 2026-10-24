"""Record deterministic external events and complete CPU snapshots."""
import argparse
import struct
from trace.format import Trace

from .emulator import CortexM

INSTRUCTIONS = 100_000
SNAPSHOT_WORDS = 17


def _validate_real_events(build_id, events):
    trace = Trace(build_id, events)
    trace.encode()
    unsupported = [event[0] for event in trace.events if event[0] not in (1, 2, 3)]
    if unsupported:
        raise ValueError(f"real ELF replay does not support event tag {unsupported[0]}")
    return trace.events


def apply_real_event(cpu, event):
    kind = event[0]
    if kind == 1:
        cpu.inject_irq(event[2])
    elif kind == 2:
        cpu.queue_read_override(event[2], event[3], event[4])
    elif kind == 3:
        if event[3] != len(event[4]):
            raise ValueError("DMA declared length does not match payload")
        cpu.dma(event[2], event[4])
    else:
        raise ValueError(f"real ELF replay does not support event tag {kind}")


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
        item = tuple(event)
        _validate_real_events(self.cpu.build_id, [item])
        if item[1] < self.cpu.count:
            raise ValueError("cannot schedule an event in the past")
        candidate = self.events + [item]
        candidate.sort(key=lambda item: (item[1], item[0]))
        self.events = _validate_real_events(self.cpu.build_id, candidate)

    def step(self):
        point = self.cpu.count
        for event in self.events:
            if event[1] != point:
                continue
            apply_real_event(self.cpu, event)
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
        return Trace(self.cpu.build_id, self.events)


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
