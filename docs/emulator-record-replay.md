# Emulator, recording, and replay

## Host choices

| Host | Role | Strength | Explicit limitation |
|---|---|---|---|
| QEMU 11.0.3 | `mps2-an385` boot smoke | boots genuine Cortex-M3 image | no exact retirement callback, 17-field post-retire snapshot, MMIO read override, or count-indexed IRQ |
| Unicorn 2.1.4 | deterministic execution | one-instruction `emu_start`, register reads, hooks | no board/peripheral contract |
| `replay/model.py` | unit model | compact state+memory checks | not the real Cortex-M result |

## Recording algorithm

1. Hash the ELF with SHA-256 for `build_id`.
2. Load ELF32 loadable segments and vector-table SP/PC.
3. Before each step, apply events whose instruction count equals `cpu.count`.
4. Execute exactly one instruction, including the narrow exception return shim.
5. Save R0–R12, SP, LR, PC, xPSR: exactly 17 fields.
6. Encode events as DTRC v2 with CRC32.

## IRQ shim

`inject_irq(irq)` looks up the handler at vector-table offset `4*(16+irq)` and clears its Thumb bit for the handler PC. It writes a synthetic 8-word frame containing `R0-R3/LR/PC/xPSR` with the layout `R0-R3/R12/LR/PC/xPSR`, decrements SP by 32 bytes, sets `LR=0xfffffff9`, and enters the handler. The custom `bx lr` path restores that frame and returns to the saved PC. This is not native Unicorn Cortex-M exception semantics: there is no hardware stacking, priorities, masking, nested IRQ handling, or general NVIC model.

## Branch PC ceiling

`recorder/emulator.py` hardcodes two post-step PC redirects for the current `race.elf` control-flow shape: after retiring at `0x70` with the Z flag set, PC becomes `0x64`; after retiring at `0x78`, PC becomes `0x64`. Those addresses are build-dependent and are an explicit Phase-0 ceiling, not a general Thumb branch decoder. Rebuilds that move the race loop must update the patch sites or replace them with a disassembly-driven approach before treating PC maps in [firmware-race.md](firmware-race.md) as current.

## Replay and comparison

`replay(trace, steps, elf)` rejects build mismatch, applies tags at matching counts, and returns one checked 17-field tuple per step. `first_divergence` scans paired states and reports instruction index, event index, expected/actual state, and nearby events. `tools/differ.py` adds source disassembly when an ELF and PC are available.

```python
from replay.engine import replay, first_divergence
states = replay(trace, 20, elf="firmware/build/race.elf")
report = first_divergence(expected, states, trace.events)
```

## Evidence and limits

The real campaign passes 100,000/100,000 states; clean and corrupt schedule 4 each replay 20/20. The model's state+memory representation must not be described as the real 17-field snapshot. No wall-clock throughput is inferred because instruction count is not an emulated timebase.
