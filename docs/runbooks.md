# Runbooks

## Clean host verification

```sh
python3 -m venv .venv  # only if .venv is absent
.venv/bin/pip install -r requirements.txt
make demo
make check
make evidence
```

Expected: `make demo` locks seed 0 at `corruptions=2` and replays one corrupting schedule; unit/replay tests pass; model demo reports 66 bytes/7 events; race seeds report 2/1/2/1. Do not replace missing Verilator with a synthetic simulator.

## RTL and P&R

```sh
make rtl-test
make gateway-test
make synth
PATH=/tmp/nextpnr-build:$PATH make pnr
```

Use the `/tmp/nextpnr-build` PATH prefix unless `nextpnr` is globally installed. Inspect `gateway/build/synth.log` and `gateway/build/pnr.log`. P&R warnings are expected because I/O constraints are intentionally incomplete.

## Troubleshooting

| Symptom | Cause | Action |
|---|---|---|
| `check blocked` | missing venv or Verilator | create `.venv`; install toolchain; retry |
| build-ID mismatch | trace and ELF differ | record and replay against same ELF |
| checksum/ordering error | corrupted or noncanonical DTRC | regenerate; inspect with `Trace.decode` |
| overflow asserted | producer outran storage | discard capture, reset, reduce source rate; do not accept partial trace |
| nextpnr missing | not on PATH | build in `/tmp/nextpnr-build`, prepend PATH |
| unconstrained-I/O warnings | provisional LPF | expected until hardware handoff selects pins |

## Reporting rule

Paste actual command output into issue/JOURNAL entries. Keep numeric claims in [verification.md](verification.md), wire claims in [trace-format.md](trace-format.md), and physical tasks in [hardware-handoff.md](hardware-handoff.md).
