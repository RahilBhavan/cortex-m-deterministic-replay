# Emulator, recording, and replay

This page explains why Unicorn is the instruction core, how the recorder injects events, and how replay finds the first divergence.

## Host choices

| Host | Role | Strength | Explicit limitation |
|---|---|---|---|
| QEMU 11.0.3 | `mps2-an385` boot smoke | boots genuine Cortex-M3 image | no exact retirement callback, 17-field post-retire snapshot, MMIO read override, or count-indexed IRQ |
| Unicorn 2.1.4 | deterministic execution | one-instruction `emu_start`, register reads, hooks | no board/peripheral contract |
| `replay/model.py` | unit model | compact state+memory checks | not the real Cortex-M result |

## Recording algorithm

1. Hash the ELF with SHA-256 for `build_id`.
2. Load ELF32 loadable segments and vector-table SP/PC.
3. Canonicalize events by instruction point and tag; before each step, apply events whose point equals `cpu.count`.
4. Execute exactly one instruction, including the narrow exception return shim.
5. Save R0–R12, SP, LR, PC, xPSR: exactly 17 fields.
6. Encode events as DTRC v2 with CRC32.

## IRQ shim

`inject_irq(irq)` looks up the handler at vector-table offset `4*(16+irq)` and clears its Thumb bit for the handler PC. It writes a synthetic 8-word frame with layout `R0-R3/R12/LR/PC/xPSR`, decrements SP by 32 bytes, sets `LR=0xfffffff9`, and enters the handler. The custom `bx lr` path restores every owned field, including architectural PC and xPSR; a real-ELF regression checks those values independently of recorder/replayer equality. This is not native Unicorn Cortex-M exception semantics: there is no hardware stacking, priorities, masking, nested IRQ handling, or general NVIC model.

## Real event semantics

The real-ELF path supports IRQ (tag 1), one-shot read override (tag 2), and DMA memory write (tag 3). A read override must match the scheduled instruction's exact address and width; it changes the value observed by that read without persistently changing backing memory. Tags 4–7 remain valid DTRC/model-demo tags but are rejected by real replay until real semantics exist. This is supplied-event replay, not automatic peripheral capture or a peripheral model.

## Branch PC advance

Thumb-16 unconditional and conditional branches are decoded from the instruction encoding and APSR flags in xPSR (`thumb16_next_pc`). ELF symbols are loaded for diagnostics and tests (`Reset_Handler`, `Timer_Handler`, …). There are no hardcoded `0x70`/`0x78` redirect sites. Rebuilds that change the race loop still require re-validating insertion counts in [firmware-race.md](firmware-race.md). Full Thumb-32 control-flow coverage remains a documented ceiling in [ceilings.md](ceilings.md).


## Replay and comparison

`replay(trace, steps, elf)` rejects build mismatch and unsupported real tags, applies canonical tags 1–3 at matching counts, and returns one checked 17-field tuple per step. `first_divergence` scans paired states and reports instruction index, event index, expected/actual state, and nearby events. `tools/differ.py` adds source disassembly when an ELF and PC are available.

```python
from replay.engine import replay, first_divergence
states = replay(trace, 20, elf="firmware/build/race.elf")
report = first_divergence(expected, states, trace.events)
```

## Evidence and limits

The real campaign passes 100,000/100,000 states; the first corrupting schedule from seed 0 (IRQ at instruction count 4), recorded and replayed 20 times, matches 20/20. Real-ELF tests also verify architectural PC/xPSR restoration, canonical same-point IRQ/DMA ordering, DMA effects, and exact-width one-shot read overrides using values derived from the built firmware. The model's state+memory representation must not be described as the real 17-field snapshot. No wall-clock throughput is inferred because instruction count is not an emulated timebase.
