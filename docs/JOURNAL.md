# Journal

## 2026-08-06

- QEMU 11.0.3 booted the genuine Cortex-M3 image on `mps2-an385`. Available interfaces rejected exact retirement callbacks, full-register snapshots, MMIO read override, and instruction-indexed IRQ injection. The QEMU campaign stopped at that boundary; no synthetic fallback was used.
- Unicorn 2.1.4 was retained as the real instruction core with a narrow custom exception shim. It is not a board/peripheral model.
- Race campaign output for 1,000 trials and seeds 0–3 was 2, 1, 2, 1 corruptions.
- Unit/replay verification passed 20 tests, including 10,000 randomized/malformed DTRC coverage, 100,000/100,000 real 17-field replay, real MMIO divergence with disassembly, and clean/corrupt schedule replay at 20/20.
- Demo output measured 66 bytes, 7 events, 9.43 bytes/event. Bytes/sec was not derived because evidence has no modeled duration or clock contract.
- Verilator 5.050 gateway tests passed exact capture, overflow, and wrap. Yosys measured 41 LUT4, 91 FF, 2 EBR, 22 CCU2C. nextpnr measured 97 LUT4, 91 DFF, 217.58 MHz provisional Fmax at 100 MHz, and 54 unconstrained-I/O warnings.
- Dead ends: QEMU plugins/TB callbacks lack the required cross-layer controls; no bytes/sec claim is defensible. See [qemu-instrumentation.md](qemu-instrumentation.md) and [verification.md](verification.md).
