# Verification and numeric evidence

This page owns numeric evidence. Commands below are the acceptance surface; observed values are from the checked-in campaign and must not be generalized into physical performance.

| Check | Command | Observed output/result |
|---|---|---|
| Race demo | `make demo` | seed 0 `corruptions=2`; one corrupting schedule record/replay identity |
| Unit/replay | `.venv/bin/python -m unittest discover -v` | includes 10,000 codec cases, 100,000/100,000 real replay, seed-0 lock, golden stats |
| Race seed 0 | `.venv/bin/python -m recorder.race_rate --trials 1000 --seed 0` | `trials=1000 seed=0 corruptions=2` |
| Seeds 1–3 | same command with seed | corruptions `1`, `2`, `1` |
| Model demo | `.venv/bin/python -m replay.demo` | 66 encoded bytes, 7 events, 9.43 bytes/event |
| RTL | `make rtl-test && make gateway-test` | Verilator exact capture, overflow, wrap pass |
| Synthesis | `make synth` | 41 LUT4, 91 FF, 2 EBR, 22 CCU2C |
| P&R | `PATH=/tmp/nextpnr-build:$PATH make pnr` | 97 LUT4, 91 DFF, 217.58 MHz provisional, 54 warnings |

## Evidence blocks

> **Measured:** 10,000 randomized DTRC round trips; malformed and boundary rejection; 100,000 real 17-field replay; 20/20 clean and corrupt schedule replay.

> **Not measured:** bytes/sec, physical ETM capture, sustained DDR throughput, board timing, pin legality, reset/CDC behavior on silicon. See [ceilings.md](ceilings.md).

The 66-byte number is a stream-size observation. Dividing by seven gives 9.43 bytes/event; dividing by seconds is intentionally omitted because no modeled duration or clock contract exists.
