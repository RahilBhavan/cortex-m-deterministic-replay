# Runbooks

## Clean host verification

```sh
python3 -m venv .venv  # only if .venv is absent
.venv/bin/pip install -r requirements.txt
make demo
make check
make evidence
make rtl-lint
```

Expected: `make demo` locks seed 0 at `corruptions=2` and replays one corrupting schedule; 39 unit/replay tests pass; the checked-in 66-byte golden trace crosses the Icarus FIFO and Verilator capture gate exactly; model demo reports 66 bytes/7 events; race seeds report 2/1/2/1. Do not replace missing tools with fabricated output.

## RTL and P&R

```sh
make rtl-test
make gateway-test
make rtl-lint
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
| unsupported real tag | tags 4–7 are model-only | use tags 1–3 for real ELF replay or add explicit real semantics first |
| read override mismatch | scheduled instruction used a different address/width | derive the real access point and width from the built ELF |
| overflow asserted | producer outran storage | discard capture, reset, reduce source rate; do not accept partial trace |
| nextpnr missing | not on PATH | build in `/tmp/nextpnr-build`, prepend PATH |
| unconstrained-I/O warnings | provisional LPF | expected until hardware handoff selects pins |

## Reporting rule

Paste actual command output into issue/JOURNAL entries. Keep numeric claims in [verification.md](verification.md), wire claims in [trace-format.md](trace-format.md), and physical tasks in [hardware-handoff.md](hardware-handoff.md).
