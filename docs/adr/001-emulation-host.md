# ADR 001: emulation host

Use a small Python deterministic model for Phase 0. Renode and QEMU provide useful integration targets but do not uniformly expose exact retired instruction hooks plus MMIO injection on macOS; Unicorn lacks peripherals. The model makes the contract testable without external packages.
