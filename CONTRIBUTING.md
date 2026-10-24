# Contributing

## Bootstrap

```sh
make setup
make firmware
make demo
```

Host unit tests:

```sh
.venv/bin/python -m unittest discover -v
```

Full gate (needs Verilator on PATH):

```sh
make check
make evidence
```

CI note: GitHub Actions runs `host-tests` as the badge gate with a checksum-verified Arm GNU Toolchain and blocking golden-DTRC/Icarus transport test. `rtl-verilator` remains best-effort (`continue-on-error`). Prefer measured host evidence when quoting CI green.

## What to claim

Keep numeric claims aligned with [docs/verification.md](docs/verification.md). Do **not** invent:

- bytes/sec without an explicit duration/clock contract
- board timing from provisional nextpnr Fmax
- physical ETM or sustained capture results from host/RTL simulation

Physical acceptance lives in [docs/hardware-handoff.md](docs/hardware-handoff.md) and stays unchecked until silicon evidence exists.

## Layout

| Path | Owns |
|---|---|
| `firmware/` | race workload ELF |
| `recorder/` | Unicorn core + record path |
| `replay/` | replay engine and model demo |
| `trace/` | DTRC v2 codec |
| `gateway/` | SystemVerilog capture path |
| `tools/` | differ, stats, race demo CLI |
| `tests/` | unittest suite |
| `docs/` | architecture, evidence, handoff |

## Style

- Prefer measured command output over narrative estimates.
- Keep supplied read-override/DMA replay distinct from automatic peripheral or physical capture.
- Document ceilings (IRQ shim ≠ NVIC, incomplete Thumb-32 beyond the race ELF, provisional LPF / unconstrained I/O, no bytes/sec) instead of hiding them. Hardcoded `0x70`/`0x78` branch redirects were removed; do not reintroduce them.
- Do not commit `.venv/`, `firmware/build/`, `gateway/build/`, or `obj_dir/`.
