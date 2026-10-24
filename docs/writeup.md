# Blog / LinkedIn writeup — Phase 0

Copy, trim, or split for a blog post and a LinkedIn post. Claims match [verification.md](verification.md) and [ceilings.md](ceilings.md).

---

## LinkedIn (short)

I open-sourced Phase 0 of a deterministic record/replay debugger for Cortex-M firmware — think `rr`, but for bare-metal.

The idea: you do not need full instruction trace. You need every source of nondeterminism (IRQs, MMIO reads, DMA) recorded at **instruction-count** granularity, then injected on replay until register state matches bit-for-bit.

What shipped:

- Real Cortex-M3 race firmware + Unicorn recorder/replayer (17-field snapshots, architectural PC/xPSR IRQ-return check)
- CRC-validated DTRC v2 wire format
- Measured race rarity (seeds 0–3 → 2/1/2/1 corruptions per 1,000) and 20/20 corrupting-schedule replay
- Checked-in 66-byte DTRC transported exactly through Icarus/Verilator; reset/overflow behavior checked digitally
- Checksum-pinned host CI + `make demo`, and an explicit hardware handoff checklist (physical ETM/board work still open; broader RTL Verilator job is best-effort in CI)

I also wrote up why QEMU and Renode were the wrong Phase-0 hosts: great for boot/SoC demos, missing the retirement + count-indexed injection contract this experiment needs.

Repo: https://github.com/RahilBhavan/cortex-m-deterministic-replay  
Release: v0.1.0-phase0

---

## Blog (long)

### Title

Building an `rr` for Cortex-M: deterministic replay without lying about hardware

### Hook

Embedded races are miserable because they do not reproduce. Debuggers that depend on wall-clock timing make that worse. Deterministic replay tools like `rr` solved this on desktop Linux by recording nondeterminism. Cortex-M firmware needs the same idea with a harsher constraint: the interesting machine is often a bare-metal image, and “almost deterministic” is not good enough.

### The falsifiable claim

Capture interrupts, MMIO reads, and DMA completions at instruction-count boundaries. Replay the same ELF. Compare R0–R12, SP, LR, PC, and xPSR after every step. If those 17 fields match for 100,000 steps, the claim holds. If they diverge, a differ points at the first break.

### What Phase 0 actually built

1. **Firmware race** — a commutation invariant broken when an IRQ lands between two stores.
2. **Unicorn instruction core** — one-instruction steps, hooks, and a narrow exception shim (not a board/NVIC model).
3. **DTRC v2** — compact tagged events with CRC32 and validation.
4. **Replay + differ** — canonical IRQ/read-override/DMA replay, architectural exception-return checks, and first-divergence diagnostics with disassembly.
5. **FPGA gateway (sim)** — logical nibble assembly, reset-synchronized async FIFO, and exact checked-in-golden transport in Icarus/Verilator; physical IDDR/ETM remains future work.

### Dead ends that were worth writing down

QEMU boots the real image on `mps2-an385`, but available plugins and TCG hooks do not give retirement callbacks, full post-retire snapshots, MMIO read override, and count-indexed IRQs together.

Renode models boards and peripherals well, but Phase 0 needed retirement precision, not SoC fidelity. Optimizing the board model first would have delayed the falsifiable claim.

### Honesty as a feature

- No bytes/sec without a clock contract.
- Provisional P&R Fmax is not board timing; unconstrained I/O warnings stay in the log.
- Hardware handoff checklist starts unchecked on purpose.

### Try it

```sh
git clone https://github.com/RahilBhavan/cortex-m-deterministic-replay
cd cortex-m-deterministic-replay
make setup
make demo
```

### What’s next

Physical board bring-up: pins, ETM/trace ingress, CDC/reset validation, on-device golden DTRC, then hardware 17-field acceptance. Until then, Phase 0 stays a host-proven spine ready for integration rather than invention.
