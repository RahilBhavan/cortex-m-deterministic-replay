# Renode instrumentation investigation

Renode was evaluated as a Phase-0 emulation host and **rejected** for the deterministic record/replay contract. It remains a strong candidate for later board-level integration tests once the replay claim is proven on an instruction core.

## What Renode is good at

- Models real STM32-class boards with peripherals, memory maps, and multi-node setups.
- Scripts cleanly (Robot Framework, C#, Python monitor hooks).
- Exposes MMIO through peripheral models rather than requiring a raw bus shim.
- Runs on Apple Silicon without fighting QEMU machine bring-up for many demos.

Those strengths optimize **SoC fidelity**, not **retirement-precise nondeterminism capture**.

## Required Phase-0 controls

The recorder needs all four together:

1. Exact retired-instruction count (one architectural instruction per step).
2. Full 17-field post-retire snapshot (R0–R12, SP, LR, PC, xPSR).
3. MMIO read override at the access site (inject recorded peripheral values).
4. IRQ injection at an instruction-count index (not wall-clock or quantum time).

## Where Renode falls short for this experiment

| Need | Renode posture | Gap |
|---|---|---|
| Retirement step | Time/quantum-driven CPU blocks | No stable “retire exactly one Thumb insn then yield” API comparable to Unicorn `emu_start(..., count=1)` |
| 17-field snapshot | Monitor can dump registers | Not tied to a post-retire boundary with a single-step contract across hooks |
| MMIO override | Peripheral models own reads | Replacing an arbitrary recorded value at an arbitrary access without rewriting the peripheral is the wrong abstraction for DTRC tag 2 |
| Count-indexed IRQ | NVIC/time-based pending | IRQs are scheduled in simulated time / peripheral events, not “after instruction N” |

Renode’s NVIC and peripheral realism is therefore **more than we need for Phase 0 and less than we need for the falsifiable replay claim**. Using it first would push work into board modeling before the bit-identical Unicorn path exists.

## Decision

Keep Renode out of Phase-0 evidence. Document the rejection here and in [adr/001-emulation-host.md](adr/001-emulation-host.md). Revisit Renode when:

- the Unicorn DTRC/replay contract is stable, and
- the next risk is peripheral accuracy or multi-device scenarios rather than retirement control.

## Contrast with QEMU and Unicorn

| Host | Verdict | One-line reason |
|---|---|---|
| QEMU | boot smoke only | no combined retirement + MMIO override + count-IRQ controls ([qemu-instrumentation.md](qemu-instrumentation.md)) |
| Renode | deferred | SoC-oriented; no Phase-0 retirement contract |
| Unicorn | Phase-0 core | one-instruction step + hooks; narrow IRQ shim; not a board |

## Reproduction note

This investigation is a design evaluation, not a measured Renode campaign. No Renode race/replay numbers are claimed. Install and explore locally if desired:

```sh
# illustrative only — not part of make check / CI
renode --version
```
