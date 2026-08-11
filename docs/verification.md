# Verification and numeric evidence

This page owns numeric evidence. Commands below are the acceptance surface; observed values are from the checked-in campaign and must not be generalized into physical performance.

| Check | Command | Observed output/result |
|---|---|---|
| Race demo | `make demo` | seed 0 `corruptions=2`; one corrupting schedule record/replay identity |
| Unit/replay | `.venv/bin/python -m unittest discover -v` | 39 tests; includes golden codec identity, 10,000 parser-property cases, 100,000/100,000 real replay, architectural IRQ return, same-point ordering, real DMA/one-shot read override, seed-0 lock |
| Race seed 0 | `.venv/bin/python -m recorder.race_rate --trials 1000 --seed 0` | `trials=1000 seed=0 corruptions=2` |
| Seeds 1–3 | same command with seed | corruptions `1`, `2`, `1` |
| Model demo | `.venv/bin/python -m replay.demo` | 66 encoded bytes, 7 events, 9.43 bytes/event |
| Golden RTL FIFO | `.venv/bin/python -m unittest tests.test_end_to_end -v` | checked-in 66-byte DTRC round-trips byte-for-byte through Icarus |
| RTL | `make rtl-test && make gateway-test && make rtl-lint` | Verilator golden capture, depth-2 async FIFO, overflow freeze, reset recovery, wrap; lint/Yosys checks pass |
| Synthesis | `make synth` | 41 LUT4, 93 FF, 2 EBR, 22 CCU2C |
| P&R | `PATH=/tmp/nextpnr-build:$PATH make pnr` | 111 TRELLIS_COMB, 93 TRELLIS_FF, 211.42 MHz provisional, 54 warnings |

## Evidence blocks

> **Measured:** exact checked-in golden DTRC codec/RTL transport; 10,000 deterministic parser-property round trips plus malformed/boundary rejection; 100,000 real 17-field replay; architectural IRQ return; real-ELF DMA/read override; 20/20 corrupting-schedule replay.

> **Not measured:** bytes/sec, physical ETM capture, sustained DDR throughput, board timing, pin legality, reset/CDC behavior on silicon. See [ceilings.md](ceilings.md).

The 66-byte number is a stream-size observation. Dividing by seven gives 9.43 bytes/event; dividing by seconds is intentionally omitted because no modeled duration or clock contract exists.
