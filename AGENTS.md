## Learned User Preferences
- Prefers plan-first workflows; when implementing an attached plan, complete all existing todos without recreating them or editing the plan file.
- Prefers extreme detail and thorough coverage when assessing resume readiness, explaining the project, or preparing for interviews.
- Treats documented hardware and emulator fidelity gaps as known ceilings to document honestly, not as unfinished features blocking resume use.
- Wants interview-ready explanations of the project at multiple depth levels, including interactive or textbook-style learning materials when asked.

## Learned Workspace Facts
- This repository is Deterministic Cortex-M Trace and Replay (DTRC): an rr-style record/replay debugger for Cortex-M firmware using CRC-validated DTRC v2 traces.
- Major subsystems include `firmware/`, `recorder/`, `replay/`, `trace/`, `tools/`, `gateway/` (RTL/Verilator), and `tests/`; phase-0 evidence runs on the host and does not claim physical-board capture.
- Public remote is `RahilBhavan/cortex-m-deterministic-replay` with GitHub Actions CI; packaging includes LICENSE, CONTRIBUTING, and demo assets under `docs/assets/`.
- Canonical docs for architecture, verification, demo script, and explicit ceilings live under `docs/` (notably `docs/ceilings.md` and `docs/demo-script.md`). Resume bullets and interview notes are kept outside this public tree.
- Documented known ceilings include Unicorn not equaling board/NVIC fidelity, incomplete Thumb-32 beyond the race ELF, provisional P&R with unconstrained I/O, and no sustained bytes/sec claim; hardcoded `0x70`/`0x78` PC redirects were removed via Thumb-16 decode.

## Custom agents
- `cortex-replay`: firmware, recorder, and replay emulator correctness; delegates DTRC codec work to `trace-protocol` and RTL work to `rtl-gateway`.
- `trace-protocol`: DTRC serialization, protocol consumers, and tests.
- `rtl-gateway`: gateway SystemVerilog, Verilator checks, and synthesis boundaries.
- All agents must preserve the documented ceilings: no unsupported physical-board/ETM, NVIC-fidelity, sustained-bandwidth, or board-timing claims.
