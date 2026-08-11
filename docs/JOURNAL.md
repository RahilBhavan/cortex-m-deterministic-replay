# Journal

## 2026-08-11

- Restored architectural PC and xPSR on the narrow synthetic IRQ return and added an independent full-snapshot regression against the real race ELF.
- Canonicalized equal-point event application before recording; real replay now supports tags 1–3, rejects model-only tags 4–7, and checks one-shot read address/width. Added real-ELF DMA and read-override coverage derived from live ELF state.
- Tightened DTRC tuple arity and bytearray normalization; the checked-in 66-byte golden now round-trips exactly through the codec and blocking Icarus RTL FIFO test.
- Added reset synchronizers, depth-2 async FIFO coverage, overflow freeze/recovery, golden-driven Verilator capture, and static RTL checks. Fresh synthesis reports 41 LUT4, 93 FF, 2 EBR, 22 CCU2C.
- Fresh provisional P&R reports 111 TRELLIS_COMB, 93 TRELLIS_FF, 211.42 MHz at a 100 MHz target, and 54 unconstrained-I/O warnings; this remains a tool estimate, not board timing.
- Pinned host CI to Ubuntu 24.04, immutable action commits, and checksum-verified Arm GNU Toolchain 15.2.Rel1. Two clean pinned builds matched at ELF SHA-256 `2b80cc25240e253f33a88076aa46639829b31167c577e92d275338a42c1f72d1`; 39 tests passed against that ELF.

## 2026-08-07

- Resume-readiness polish: removed unverified “clean 20/20” wording from evidence owners; fixed demo-script unittest path; refreshed resume bullets / cheat sheet; clarified host-vs-RTL CI contract.
- Replaced hardcoded `0x70`/`0x78` branch redirects with Thumb-16 decode + ELF symbol diagnostics; 32 unit tests pass.
- Added ceilings page, Renode investigation, demo GIF/cast assets, and blog/LinkedIn writeup copy.
- Phase-0 tree published earlier the same day as `v0.1.0-phase0` with green host+RTL CI.

## 2026-08-06

- QEMU 11.0.3 booted the genuine Cortex-M3 image on `mps2-an385`. Available interfaces rejected exact retirement callbacks, full-register snapshots, MMIO read override, and instruction-indexed IRQ injection. The QEMU campaign stopped at that boundary; no synthetic fallback was used.
- Unicorn 2.1.4 was retained as the real instruction core with a narrow custom exception shim. It is not a board/peripheral model.
- Race campaign output for 1,000 trials and seeds 0–3 was 2, 1, 2, 1 corruptions.
- Unit/replay verification passed 20 tests, including 10,000 randomized/malformed DTRC coverage, 100,000/100,000 real 17-field replay, real MMIO divergence with disassembly, and corrupting-schedule replay at 20/20.
- Demo output measured 66 bytes, 7 events, 9.43 bytes/event. Bytes/sec was not derived because evidence has no modeled duration or clock contract.
- Verilator 5.050 gateway tests passed exact capture, overflow, and wrap. Yosys measured 41 LUT4, 91 FF, 2 EBR, 22 CCU2C. nextpnr measured 97 LUT4, 91 DFF, 217.58 MHz provisional Fmax at 100 MHz, and 54 unconstrained-I/O warnings.
- Dead ends: QEMU plugins/TB callbacks lack the required cross-layer controls; no bytes/sec claim is defensible. See [qemu-instrumentation.md](qemu-instrumentation.md) and [verification.md](verification.md).
