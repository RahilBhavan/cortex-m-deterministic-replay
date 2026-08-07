# Build Prompt — Phase 0 (macOS, zero hardware)

Paste everything below the line into a fresh Claude Code session, run from the project
root. It is written to be self-contained.

---

## Project

Build the software spine of an open **deterministic record/replay debugger for Cortex-M
firmware** — an `rr` for embedded. No hardware is available yet; boards are on order.
Everything in this phase runs on an Apple Silicon MacBook against an emulator, so that
when hardware arrives the work is *integration*, not *invention*.

The novel contribution of this project is the replay engine, and it is pure software.
That is what we build now.

### The core idea

Deterministic replay does not require instruction trace. It requires capturing every
source of **nondeterminism** and injecting the recorded values back on replay. On a
Cortex-M there are exactly three:

1. **Interrupt arrival** — must be recorded at *instruction-count* granularity, not
   wall-clock time. An interrupt that fired after the 10,472nd instruction must fire
   after the 10,472nd instruction on replay, every time.
2. **Peripheral MMIO reads** — reading a status register returns a different value each
   run. Record the value returned at each read site + execution point.
3. **DMA completion** — asynchronous memory writes the CPU did not perform.

Record those three, replay the program, and execution is bit-identical. That claim is
the whole project, and it is falsifiable — which is what makes it good.

## Phase 0 goals

Deliver, all validated in emulation:

1. **Toolchain + emulator harness** that runs bare-metal Cortex-M firmware on macOS ARM64
   and can single-step, count instructions, and observe MMIO accesses.
2. **A demo firmware workload** with a deliberate, real race condition that reproduces
   intermittently (target: roughly 1-in-500 runs).
3. **The recorder** — captures the three nondeterminism sources into a compact trace
   format.
4. **The replay engine** — re-executes the firmware, injecting recorded values, and
   produces a bit-identical register/memory trace.
5. **A golden-trace differ** that proves fidelity or localizes the first divergence.
6. **The FPGA capture gateware, simulated only** — written and verified in Verilator,
   synthesized with yosys/nextpnr-ecp5 for resource and Fmax estimates. No board needed
   to know whether it fits and closes timing.

## Step 1 — Evaluate the emulation host before writing anything

This decision shapes everything after it. Investigate and pick, with reasons:

- **Renode** — simulates real STM32 boards with peripheral models. Strong candidate
  because MMIO is already modeled and hookable, and it scripts in C#/Python.
- **QEMU** — check which Cortex-M machines exist (`mps2-an500`, `netduinoplus2`,
  `olimex-stm32-h405`, `lm3s6965evb`). Investigate `-icount` for deterministic
  instruction counting and QEMU's built-in record/replay (`-record`/`-replay`) — note
  what it does and does not cover for Cortex-M, since it may solve part of this for us
  or may be a dead end worth documenting.
- **Unicorn Engine** — raw CPU emulation, no peripherals. Maximum control, most work.

Selection criteria, in priority order: (a) can we get an exact retired-instruction count?
(b) can we hook every MMIO read and write? (c) can we inject values on replay? (d) does it
build and run on Apple Silicon without fighting it?

Write the decision and the rejected alternatives into `docs/adr/001-emulation-host.md`
before proceeding. If none of the three cleanly supports (a)+(b)+(c), say so explicitly
and propose the smallest patch or shim that does — that finding is itself valuable.

## Step 2 — Repository layout

Create this structure. Keep it flat; do not add abstraction layers that have one
implementation.

```
firmware/          bare-metal Cortex-M demo target (C, arm-none-eabi-gcc)
  src/
  linker/
  Makefile
recorder/          host-side recorder (Python or Rust — justify the choice)
replay/            host-side replay engine
trace/             trace format definition + codec, shared by recorder and replay
gateway/           FPGA capture gateware (Verilog) + Verilator testbenches
  rtl/
  sim/
tools/             differ, analysis scripts, plotting
docs/
  adr/             architecture decision records
tests/
```

## Step 3 — Demo firmware with a real race

Write a small motor-control-shaped workload in `firmware/`: a timer ISR updating a
commutation state machine, a main loop reading and acting on that state, and a
deliberately unguarded shared structure between them. The bug must be a *genuine* race —
a torn read of a multi-word state, or a check-then-act on a flag the ISR clears — not an
artificial `sleep()`.

**Acceptance:** running it 1000 times in the emulator with varied interrupt timing
produces the corrupted outcome in roughly 1 to 5 runs per thousand. Report the actual
rate. If it fires every run it is too easy; if it never fires it is untestable.

Note in the README that this stands in for a BLDC controller until hardware arrives, and
that the same firmware is intended to run on the real board later.

## Step 4 — Trace format

Define a compact binary format in `trace/`. Requirements:

- Interrupt events: `(instruction_count, irq_number)`
- MMIO reads: `(instruction_count, address, value_returned, access_width)`
- DMA completions: `(instruction_count, target_address, length)` plus payload or a hash
- Self-describing header with firmware build ID, so a trace cannot be replayed against a
  different binary and silently produce nonsense

Prioritize compactness — on real hardware this must survive a bandwidth-limited link.
Report measured bytes-per-second for the demo workload; that number sets the hardware
requirement later. Use delta encoding on instruction counts.

**Acceptance:** round-trip encode/decode is lossless over randomized synthetic traces
(property test, 10k cases).

## Step 5 — Recorder and replay engine

The recorder hooks the emulator and writes a trace. The replay engine re-runs the same
firmware image, and at each recorded execution point injects the recorded value instead of
letting the emulator produce a fresh one.

**Acceptance — this is the project's core claim, so make it precise:**

1. Record a 100k-instruction run.
2. Replay it.
3. The full register file (R0-R12, SP, LR, PC, xPSR) at *every* retired instruction must
   be bit-identical between record and replay. Not "the output matches" — the register
   trace matches.
4. On divergence, the differ in `tools/` must report the first differing instruction
   index, both register states, and the disassembly at that PC. Debuggability of your own
   tool matters here; you will use this constantly.

Then the demo that sells the whole project:

5. Catch a run where the race fires. Replay it **20 out of 20 times** with identical
   outcome. Report both the live reproduction rate and the replay rate.

## Step 6 — FPGA gateware, simulated

In `gateway/`, write the trace-capture front end targeting Lattice ECP5, buildable with
the fully open toolchain (yosys + nextpnr-ecp5 + Project Trellis, all of which install on
Apple Silicon via oss-cad-suite).

Scope for now:
- Source-synchronous DDR sampling of a 4-bit trace data bus plus clock
- Deep FIFO with CDC into a host-transfer clock domain
- Overflow detection and reporting — **a silently dropped packet destroys replay
  fidelity, so dropping must be detected and surfaced, never absorbed**

**Acceptance:**
- Verilator testbench feeds a synthetic DDR trace pattern; the captured byte stream
  matches the input exactly at target rate, and overflow is correctly flagged when the
  host drain is throttled.
- `yosys` + `nextpnr-ecp5` report resource usage and Fmax for the target part. Record
  both in `docs/`. We need to know now whether this closes timing at 100+ MHz, not after
  the board arrives.

## Step 7 — Documentation as you go

Keep `docs/adr/` current — one short record per real decision. Keep a `docs/JOURNAL.md`
with dated entries including **dead ends and things that did not work**. This is not
ceremony: the commit history and the record of failures are a credibility artifact for
this project's actual purpose, and reconstructing them later is impossible.

## Constraints and style

- macOS ARM64 (Apple Silicon). Everything must work here — no Docker-only paths, no
  x86-only tools.
- Free and open toolchain only: `arm-none-eabi-gcc`, `openocd`, `oss-cad-suite`
  (yosys/nextpnr/Verilator). No Vivado, no vendor licenses.
- Prefer stdlib and already-installed dependencies. Do not add a package for something a
  few lines cover.
- No abstraction with a single implementation. No configuration for a value that never
  changes. No scaffolding "for later."
- Every non-trivial piece of logic leaves behind one runnable check — the smallest thing
  that fails if the logic breaks. Not a test framework build-out.
- Mark deliberate shortcuts with a `ponytail:` comment naming the ceiling and the upgrade
  path.

## What NOT to build in this phase

- No GUI, no web dashboard, no VS Code extension.
- No support for chips we do not have.
- No performance optimization before the fidelity claim is proven. Correct first; a
  replay engine that is fast and wrong is worthless.
- Do not attempt ETM instruction-trace decoding yet. The nondeterminism-source approach
  above is the primary path and does not need it. ETM is a later scope upgrade, and it may
  turn out to be unnecessary — which would be a finding worth publishing.

## First actions

1. Verify the toolchain installs and runs on this machine; report versions.
2. Do Step 1 and write the ADR. **Stop and report the emulator decision before building
   on top of it** — if that choice is wrong everything downstream is wasted.
