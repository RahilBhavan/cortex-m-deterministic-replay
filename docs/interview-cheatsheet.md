# Interview cheat sheet

One page for live interviews. Numbers live in [verification.md](verification.md). Honesty contract: [ceilings.md](ceilings.md). Full talk track: [demo-script.md](demo-script.md).

## 30 seconds

Phase-0 `rr`-style record/replay for bare-metal Cortex-M on a **Unicorn instruction core** (not a board): capture IRQ/MMIO/DMA into CRC’d DTRC v2, replay a real ELF with bit-identical 17-field snapshots (100k/100k). Verilator-validated capture gateware; provisional P&R and hardware handoff explicitly unfinished.

## 5 minutes

1. Problem → instruction-count nondeterminism (`demo-script.md` §1).
2. `make demo` → seed 0 `corruptions=2`, corrupting schedule identity (`demo-script.md` §2).
3. 17 fields / optional 100k unittest (`demo-script.md` §3).
4. Differ localizes a real-ELF read-override break (`demo-script.md` §4).
5. `make gateway-test` if Verilator present (`demo-script.md` §5).
6. Open unchecked [hardware-handoff.md](hardware-handoff.md) (`demo-script.md` §6).

## Top follow-ups → one-liners

| Question | Answer | Doc |
|---|---|---|
| Why not QEMU? | Boots real image, but no combined retirement + 17-field snapshot + MMIO override + count-indexed IRQ | [qemu-instrumentation.md](qemu-instrumentation.md) |
| Why not Renode? | Strong SoC model; Phase 0 needed retirement control, not board fidelity | [renode-instrumentation.md](renode-instrumentation.md) |
| Is IRQ injection NVIC? | No — narrow `inject_irq` / `EXC_RETURN` shim only | [emulator-record-replay.md](emulator-record-replay.md), [ceilings.md](ceilings.md) |
| What are the 17 fields? | R0–R12, SP, LR, PC, xPSR | [architecture.md](architecture.md) |
| What’s DTRC v2? | Magic/`2`/build-id + tags 1–7 + CRC32; varints; strict ordering | [trace-format.md](trace-format.md) |
| Are all seven tags real-replayed? | No — real ELF supports 1–3 and rejects model-only 4–7 | [emulator-record-replay.md](emulator-record-replay.md) |
| Is the read override a peripheral? | No — one supplied value, exact instruction/address/width, no persistent peripheral model | [emulator-record-replay.md](emulator-record-replay.md) |
| What corrupts the race? | IRQ between two stores breaks a commutation invariant | [firmware-race.md](firmware-race.md) |
| Bytes/sec? | Intentionally unclaimed — no Phase-0 clock contract | [ceilings.md](ceilings.md) |
| Is Fmax board timing? | No — provisional nextpnr estimate; 54 unconstrained-I/O warnings | [rtl-results.md](rtl-results.md) |
| Hardcoded `0x70`/`0x78`? | Removed — Thumb-16 decode + symbol tests; Thumb-32 still incomplete | [ceilings.md](ceilings.md) |
| What’s left for hardware? | Pins, ETM ingress, CDC/reset, on-device golden, then timing | [hardware-handoff.md](hardware-handoff.md) |

## Do not say

- Sustained bytes/sec, board timing, native NVIC fidelity, or physical ETM capture as done.
- “Clean and corrupt 20/20” — measured claim is **corrupting-schedule 20/20** only.
- That provisional P&R proves silicon.
- That RTL reset synchronizers or simulation prove metastability behavior on silicon.
