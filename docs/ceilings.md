# Explicit ceilings

This page owns the honesty contract for Phase 0. Numbers live in [verification.md](verification.md). Physical acceptance lives in [hardware-handoff.md](hardware-handoff.md).

## Unicorn is not a board or NVIC

Unicorn 2.1.4 is the deterministic instruction core. It is **not**:

- a board or SoC model
- a peripheral model (UART, timers, DMA engines)
- a native NVIC with priorities, masking, nesting, or hardware stacking

`inject_irq` and the `BX LR` / `EXC_RETURN` path are a **narrow custom exception shim**. Race and replay evidence therefore proves the modeled schedule, not silicon IRQ latency or cache effects. Details: [emulator-record-replay.md](emulator-record-replay.md), [adr/001-emulation-host.md](adr/001-emulation-host.md).

## Thumb control flow (no hardcoded race PCs)

Branch targets for Thumb-16 `B` / `B<cond>` are decoded from the instruction encoding and APSR flags. ELF symbols (`Reset_Handler`, `Timer_Handler`, …) are loaded for diagnostics and tests. Rebuilds that change the race loop still require re-checking insertion counts in [firmware-race.md](firmware-race.md); they do **not** require editing hardcoded `0x70`/`0x78` redirects.

Remaining decode ceiling: full Thumb-32 control flow (for example every `BL`/`BLX` form) is not a complete architectural emulator. The race ELF only needs the 16-bit branch path plus the exception shim.

## Provisional P&R and unconstrained I/O

nextpnr reports ~97 LUT4, ~91 DFF, ~217.58 MHz provisional Fmax at 100 MHz with **54 unconstrained-I/O warnings**. The LPF only constrains `clk`. That Fmax is a **tool estimate**, not board timing. Pin legality, I/O standards, and independent-clock CDC on silicon remain unchecked in [hardware-handoff.md](hardware-handoff.md). See [rtl-results.md](rtl-results.md).

## No bytes/sec claim

The 66-byte / 7-event demo is a **stream-size** observation (9.43 bytes/event). Dividing by wall-clock or inventing an emulated duration is forbidden: there is no Phase-0 clock contract for host instruction count. `tools/trace_stats.py --seconds` only computes a workload ratio when the operator supplies an explicit duration and must not be quoted as hardware bandwidth.

## Summary table

| Topic | Status | Where enforced |
|---|---|---|
| Unicorn ≠ board/NVIC | ceiling | this page; ADR 001; emulator docs |
| Hardcoded race branch PCs | **removed** | Thumb-16 decode + symbol tests |
| Provisional P&R / unconstrained I/O | ceiling | rtl-results; hardware-handoff |
| bytes/sec | intentionally unclaimed | verification; trace_stats disclaimer |
