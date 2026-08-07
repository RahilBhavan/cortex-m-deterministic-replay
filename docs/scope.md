# Scope

Phase 0 validates deterministic capture, injection, and diagnostics for Cortex-M firmware on a host instruction core.

The real evidence path is Unicorn 2.1.4 with a narrow exception shim: record IRQ/MMIO/DMA nondeterminism into DTRC v2, replay the genuine ELF, and compare 17-field snapshots. `replay/model.py` is a compact unit model only and is not the real Cortex-M result. This repository is not a full ARM board/peripheral emulator and does not claim physical ETM capture, board timing, or sustained bandwidth.
