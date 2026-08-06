# Deterministic Cortex-M Trace

This repository is a synthetic, MacBook-first vertical slice for deterministic Cortex-M-like trace capture and replay. It is not the completed full BUILD_PROMPT Phase 0: the model and FIFO stand in for firmware and hardware while the remaining validation work is tracked in [docs/ROADMAP.md](docs/ROADMAP.md).

## Architecture and data flow

```text
trace events -> Trace.encode + CRC32 -> raw ordered bytes -> RTL FIFO -> raw ordered bytes
     |                                                        |
     +-> deterministic model replay <- Trace.decode + CRC32 <-+
                                      -> divergence diagnostics
```

The host model and RTL transport do not claim physical ETM capture. See [docs/trace-format.md](docs/trace-format.md) and [docs/hardware-boundary.md](docs/hardware-boundary.md).

## Setup and run

From the repository root:

```sh
python3 -m unittest discover -v
python3 -m replay.demo
make check
```

On macOS, install the RTL simulator used by the checked-in end-to-end test with:

```sh
brew install icarus
```

`make check` intentionally requires Icarus or Verilator. Host-only validation is the first two commands above; full validation adds the RTL simulation. See [docs/macos-setup.md](docs/macos-setup.md).

## Current verified results

- 8 unittest cases pass.
- The demo reports bit-identical model replay and a deliberate divergence diagnostic.
- Icarus RTL simulation passes through `make check`.

No Verilator, yosys, or nextpnr result is claimed. Limitations include the synthetic Cortex-M-like model, no completed firmware/emulator race validation, no board or DDR/CDC capture path, and no FPGA synthesis or timing result. The prioritized remaining work is in [docs/ROADMAP.md](docs/ROADMAP.md).
