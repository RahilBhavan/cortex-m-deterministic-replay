# Resume bullets

Paste-ready lines. Numbers match [verification.md](verification.md). Do not upgrade provisional P&R into board timing.

## Short

- Built Phase-0 of an `rr`-style deterministic record/replay path for Cortex-M firmware on a Unicorn instruction core: captured IRQ/MMIO/DMA nondeterminism into a CRC-validated DTRC v2 trace and replayed a real ELF with bit-identical 17-field register snapshots (100,000/100,000).

## Medium

- Designed DTRC v2 (7 event tags, varints, CRC32) with 10,000 randomized encode/decode round trips and malformed-input rejection.
- Implemented a Unicorn 2.1.4 Cortex-M recorder/replayer with canonical instruction-point IRQ/read-override/DMA injection and architectural PC/xPSR return checks (narrow exception shim, not a board/NVIC model); measured a bare-metal commutation race at seeds 0–3 (2/1/2/1 corruptions per 1,000) and replayed the first corrupting schedule bit-identically in 20 of 20 repeats.
- Wrote SystemVerilog capture gateware (logical nibble packing + async FIFO), transported the checked-in 66-byte DTRC exactly in Icarus/Verilator, verified overflow freeze/reset recovery, and ran open ECP5 synthesis (41 LUT4, 93 FF, 2 EBR, 22 CCU2C) with physical pin/CDC handoff still unchecked.

## Depth / interview follow-ups

- Documented a QEMU instrumentation dead-end (no combined retirement callback + 17-field snapshot + MMIO override + count-indexed IRQ) and rejected Renode for Phase 0 because the missing contract was instruction-core control, not SoC modeling ([renode-instrumentation.md](renode-instrumentation.md)).
- Kept claims falsifiable: no bytes/sec without a clock contract; provisional P&R warnings left visible; hardware checklist unchecked until on-device golden streams exist ([ceilings.md](ceilings.md)).
- Replaced hardcoded race branch PC redirects with Thumb-16 decode + ELF symbol diagnostics; remaining decode ceiling is incomplete Thumb-32 beyond the race ELF’s needs ([ceilings.md](ceilings.md)).
