# ADR 001: emulation host

**Status:** accepted for Phase 0.

## Decision

Use QEMU 11.0.3 on `mps2-an385` as the genuine-firmware boot-smoke host. Use Unicorn 2.1.4 as the deterministic instruction core for recording and replay, with only a narrow custom exception shim. Do not describe Unicorn as a board/peripheral model. Renode was evaluated and rejected for Phase 0 (see [renode-instrumentation.md](../renode-instrumentation.md)).

## Rationale

The experiment requires one retirement step, all 17 register fields, MMIO read override, and IRQ injection at an instruction count. QEMU's available hooks do not supply that complete contract ([qemu-instrumentation.md](../qemu-instrumentation.md)). Renode is strong for STM32 board/peripheral scripting, but Phase 0 needs exact retired-instruction control and count-indexed IRQ/MMIO injection rather than a full SoC model; adopting Renode would optimize the wrong layer before the replay contract is proven. `replay/model.py` is not an acceptable fallback for real-firmware evidence because it is model state plus memory rather than a Cortex-M snapshot.

## Consequences

Host evidence is limited to Unicorn-backed campaigns: race seeds 0–3 yield 2/1/2/1 corruptions per 1,000; real replay passes 100,000/100,000. QEMU remains useful as a boot boundary. Renode is deferred until peripheral/board fidelity becomes the next risk. Any future QEMU or Renode implementation must add and validate the missing cross-layer retirement controls before replacing this decision.
