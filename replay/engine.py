"""Replay DTRC traces against the real Cortex-M emulator."""
from replay.model import run as model_run
from recorder.emulator import CortexM
from recorder.record import SNAPSHOT_WORDS


def _checked(state):
    if len(state) != SNAPSHOT_WORDS:
        raise ValueError("snapshot must contain 17 fields")
    return state


def _events_at(events, point):
    return [event for event in events if event[1] == point]


def replay(trace, steps=100, elf=None, expected=None):
    """Return one complete 17-register snapshot per retired instruction."""
    if elf is None:
        return model_run(steps, trace.events)
    cpu = CortexM(elf)
    if cpu.build_id != trace.build_id:
        raise ValueError("trace build ID does not match ELF")
    if expected is not None and expected != cpu.build_id:
        raise ValueError("expected build ID does not match ELF")
    states = []
    while len(states) < steps:
        for event in _events_at(trace.events, cpu.count):
            if event[0] == 1:
                cpu.inject_irq(event[2])
            elif event[0] == 2:
                cpu.mmio[event[2]] = event[3]
            elif event[0] == 3:
                cpu.dma(event[2], event[4])
        states.append(_checked(cpu.step()))
    return states


def first_divergence(expected, actual, events=()):
    n = min(len(expected), len(actual))
    for index in range(n):
        if expected[index] != actual[index]:
            return _difference(index, expected[index], actual[index], events)
    if len(expected) != len(actual):
        index = n
        return _difference(index, expected[index] if index < len(expected) else None,
                           actual[index] if index < len(actual) else None, events)
    return None


def _difference(index, expected, actual, events):
    return {
        "instruction": index,
        "event_index": sum(event[1] <= index for event in events),
        "expected": expected,
        "actual": actual,
        "nearby_events": [event for event in events if abs(event[1] - index) <= 2],
    }
