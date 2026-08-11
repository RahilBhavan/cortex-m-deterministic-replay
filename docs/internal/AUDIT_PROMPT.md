# Deep Audit Prompt — Read-Only

Paste everything below the line into a fresh audit session, run from the repository root.

---

## Role and boundaries

You are a senior systems reviewer auditing an open deterministic Cortex-M record/replay debugger. Perform a deep, skeptical audit. Static inspection and inherently read-only commands must run in the original working tree; commands that can generate or overwrite artifacts must run only in a disposable mirror. Preserve every pre-existing working-tree change. Never commit, reset, checkout, stash, or alter the source tree.

Capture source-tree `git status --short` before reading and again before reporting. Any source-tree change is blocking; the final status must match the initial status. Reference repository-relative paths and line ranges, using current source anchors rather than brittle hardcoded line numbers.

Bootstrap the disposable mirror from the current working-tree contents (including untracked files), without claiming it is a Git repository:

```sh
src=$PWD
mirror=$(mktemp -d)
trap 'rm -rf "$mirror"' EXIT
rsync -a --exclude='.git/' --exclude='.venv/' --exclude='firmware/build/' --exclude='gateway/build/' --exclude='obj_dir/' "$src/" "$mirror/"
cd "$mirror"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run all mutating host, RTL, synthesis, and P&R commands from `$mirror`; use source only for static inspection and read-only commands such as `git status`, `git diff`, and `grep`. Do not use reset, checkout, or stash, and do not alter the source tree. Before reporting, return to the source tree and run `git status --short` again; remove the mirror via the trap.

Separate observed evidence from inference. Never report a check as passed unless you actually ran it and recorded its output. Never imply physical-board, ETM, NVIC, timing, sustained-throughput, or bandwidth evidence when only host emulation, RTL simulation, synthesis, or provisional P&R exists.

## Required read order and data-flow map

Read in this order:

1. `README.md`, `CONTRIBUTING.md`, `Makefile`, `docs/runbooks.md`, `docs/verification.md`, `docs/ceilings.md`, and `docs/hardware-handoff.md`.
2. Architecture decisions and project journal under `docs/adr/` and `docs/JOURNAL.md`.
3. Firmware sources, linker/build files, and generated-interface assumptions under `firmware/`.
4. Host recorder and emulator integration under `recorder/`; replay and model/demo code under `replay/`.
5. DTRC v2 definition and codec under `trace/`; differ, statistics, and evidence tools under `tools/`.
6. RTL and testbenches under `gateway/`; tests and CI workflows.

Before judging individual components, draw a concise data-flow map with file anchors:

`firmware ELF/instructions -> Unicorn execution + IRQ/MMIO hooks -> DTRC v2 events/codec -> replay injection -> register/memory traces -> differ/evidence`; include the actual DMA completion address/declared-length/payload-length/payload path, explicitly noting that DMA events encode no hash or status field and mapping any status event separately, while preserving `gateway -> raw ordered byte transport`; separately map `DDR pins -> capture -> CDC/async FIFO -> host stream -> overflow/error`, and identify every boundary where ordering, widths, clocks, checksums, build identity, or loss can be introduced.

## Checks to run

Use canonical commands from `Makefile`, `CONTRIBUTING.md`, and `docs/runbooks.md`. Perform static inspection first in the source tree. After bootstrapping the mirror above, run host checks there when prerequisites exist:

```sh
make demo
.venv/bin/python -m unittest discover -v
make evidence
```

Run the full gate in the mirror:

```sh
make check
```

Run RTL checks in the mirror only when Verilator is available, using the Makefile targets:

```sh
make rtl-test
make gateway-test
```

Synthesis and P&R are tool-gated and run in the mirror only: run only if the required tools are available; otherwise mark them skipped with the missing command/tool, never passed:

```sh
make synth
PATH=/tmp/nextpnr-build:$PATH make pnr
```

Inspect `gateway/build/synth.log` and `gateway/build/pnr.log` when those checks run. Note that incomplete I/O constraints and related P&R warnings are expected and do not establish board timing.

## Audit checklists

### Firmware, Unicorn, IRQ, and Thumb execution

- Confirm the built ELF, reset/vector assumptions, memory map, and firmware build identity are consistent with record and replay.
- Trace the actual Unicorn instruction-count mechanism and establish what “retired instruction” means, including PC/state sampling and stop boundaries.
- Check IRQ arrival ordering, instruction-point semantics, masking/nesting behavior, pending/active state, and whether the shim is a real NVIC model or only the supported demo subset.
- Check MMIO interception coverage, access width/address behavior, writes versus reads, unmapped accesses, and replay injection ordering.
- Check Thumb-16 and supported Thumb-32 decode/control-flow coverage, PC alignment, branches, calls/returns, exceptions, and unsupported-instruction behavior. Do not treat a race ELF passing as complete ISA coverage.
- Confirm DMA is either modeled and recorded correctly or explicitly absent and bounded.

### DTRC v2 codec

- Verify self-describing version/header, firmware build ID, canonical ordering, delta instruction counts, event tags, widths, payload/hash semantics, checksum/error detection, truncation handling, malformed input rejection, and boundary values.
- Compare encoder and decoder assumptions at every caller; check unknown tags and trailing data.
- Confirm tests actually cover the claimed randomized 10,000 round trips and relevant negative cases.

### Replay and differ

- Confirm replay injects recorded nondeterminism at the same execution point and rejects mismatched firmware/build IDs.
- Verify register field completeness (R0-R12, SP, LR, PC, xPSR), memory/state comparison, first-divergence localization, both states, PC disassembly, and deterministic outcome claims.
- Distinguish model/demo evidence from the real firmware replay campaign; inspect seeds and repeated replay counts.

### RTL gateway, CDC, and FIFO

- Check DDR sampling edge/bit order, byte packing, reset behavior, source/host clock-domain crossings, synchronizers, FIFO pointers/full/empty, wraparound, backpressure, overflow latching/reporting, and whether partial captures are rejected.
- Read testbench assertions and stimulus, including exact capture, throttled-drain overflow, wrap, reset, and boundary coverage. Identify simulation-only assumptions.
- Confirm synthesis top/part/tool flags and P&R constraints match the claimed target; provisional Fmax is not board timing.

### CI and reproducibility

- Inspect workflows, dependency pins, Python/tool versions, clean-checkout assumptions, artifact handling, and whether best-effort RTL status can be mistaken for a green gate.
- Reconcile CI claims with local commands and actual outputs. Flag hidden network, platform, clock, seed, generated-file, or environment dependencies.
- Check that commands are reproducible from documented setup and that committed evidence is traceable to a command and revision.

### Documentation and evidence claims

- Cross-check README, ADRs, journal, runbooks, verification, ceilings, hardware handoff, and resume/writeup claims against implementation and observed output.
- Preserve the distinction between measured host/RTL evidence and unmeasured physical claims. Explicitly flag bytes/sec, physical ETM, sustained DDR throughput, board timing, pin legality, and silicon reset/CDC claims unless direct evidence exists.
- Use these checked-in expected values only as comparison points, with the caveat that observed command output is authoritative: race seed 0 `corruptions=2`; seeds 1–3 `1,2,1`; model demo `66 encoded bytes, 7 events`; 10,000 codec cases; 100,000/100,000 replay; 20/20 corrupting-schedule replay; RTL capture/overflow/wrap pass; synthesis `41 LUT4, 93 FF, 2 EBR, 22 CCU2C`; provisional P&R `111 TRELLIS_COMB, 93 TRELLIS_FF, 211.42 MHz, 54 warnings`.

## Known informational ceilings

Treat documented ceilings as informational limitations, not bugs by themselves: the IRQ shim is not a full NVIC; Thumb-32 support is limited beyond the race ELF; LPF/I/O constraints are provisional; no bytes-per-second claim exists without a duration/clock contract; and host emulation, RTL simulation, synthesis, or provisional P&R cannot prove physical ETM capture, sustained DDR bandwidth, board timing, pin legality, or silicon reset/CDC behavior. Report a ceiling as a finding only when code or documentation contradicts it, hides it, or relies on it outside its stated scope.

## Severity rubric

- **Critical:** can silently corrupt replay evidence, lose trace data, or invalidate the central fidelity claim.
- **High:** materially breaks correctness, reproducibility, safety of capture, or a documented acceptance claim.
- **Medium:** scoped correctness gap, missing validation, or misleading evidence with a practical impact.
- **Low:** localized documentation, diagnostics, portability, or maintainability issue.
- **Informational:** limitation or improvement that does not contradict the stated scope.

## Required output

Return only an audit report, with this exact structure:

```text
# Audit Report

## Scope and execution
- Commit/revision inspected:
- Initial `git status --short`:
- Final `git status --short`:
- Commands actually run and abbreviated real outputs:
- Skipped coverage and exact reason/tool gate:

## Data-flow map
- ...

## Findings
### [SEVERITY] F-001 — Short title
- Location: `path/to/file:stable-symbol-or-nearby-line-range`
- Evidence: exact observed code, command output, or document claim
- Impact: what can be wrong or misleading
- Minimal remediation: smallest concrete fix
- Confidence: High | Medium | Low

## Claim matrix
| Claim | Source path | Supporting implementation/evidence | Status: verified / contradicted / unverified / ceiling | Gap or next check |
|---|---|---|---|---|

## Coverage and conclusion
- Subsystems reviewed:
- Checks not run:
- Most important residual risk:
```

Every finding must be line-anchored, evidence-based, minimal in remediation, and assigned confidence. Do not invent findings to fill the template. Keep skipped checks distinct from failures and do not call expected ceilings defects. End by confirming that no files were edited and whether the final git status matches the initial status.
