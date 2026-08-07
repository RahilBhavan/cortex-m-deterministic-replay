# Contributing

## Bootstrap

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
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
- Document ceilings (IRQ shim, hardcoded branch PCs, provisional LPF) instead of hiding them.
- Do not commit `.venv/`, `firmware/build/`, `gateway/build/`, or `obj_dir/`.
