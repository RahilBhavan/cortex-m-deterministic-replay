# Resume bullets

Paste-ready lines. Numbers match [verification.md](verification.md). Do not upgrade provisional P&R into board timing.

## Short

- Built an `rr`-style deterministic record/replay debugger for Cortex-M: captured IRQ/MMIO/DMA nondeterminism into a CRC’d DTRC v2 trace and replayed firmware with bit-identical 17-field register snapshots (100,000/100,000).

## Medium

- Designed DTRC v2 (7 event tags, varints, CRC32) with 10,000 randomized encode/decode round trips and malformed-input rejection.
- Implemented a Unicorn 2.1.4 Cortex-M recorder/replayer with instruction-count IRQ injection; reproduced a bare-metal commutation race at measured rarity (seeds 0–3: 2/1/2/1 corruptions per 1,000) and replayed corrupting schedules 20/20.
- Wrote SystemVerilog capture gateware (DDR nibble assembly + async FIFO), verified overflow/wrap in Verilator, and ran open ECP5 Yosys/nextpnr fit (~97 LUT4, ~218 MHz provisional Fmax) with an explicit physical pin/CDC handoff remaining.

## Depth / interview follow-ups

- Documented a QEMU instrumentation dead-end (no combined retirement callback + 17-field snapshot + MMIO override + count-indexed IRQ) and rejected Renode for Phase 0 because the missing contract was instruction-core control, not SoC modeling.
- Kept claims falsifiable: no bytes/sec without a clock contract; provisional P&R warnings left visible; hardware checklist unpublished until on-device golden streams exist.
