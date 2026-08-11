# ADR 002: gateway provisional ECP5 constraints

**Status:** accepted for synthesis and provisional P&R only.

Yosys `synth_ecp5` and nextpnr ECP5 target provisional `LFE5U-25F` / `CABGA381`. The LPF constrains only representative `clk` at 100 MHz; no pins, I/O standards, board, package legality, or hardware timing are claimed.

Observed results are 41 LUT4, 93 FF, 2 EBR, 22 CCU2C after synthesis; 111 TRELLIS_COMB, 93 TRELLIS_FF, 211.42 MHz provisional Fmax, and 54 unconstrained-I/O warnings after P&R. `gateway_top` ties capture and host clocks together only to produce a deterministic representative build. `capture_gate` still models an asynchronous FIFO path.

Before hardware use, select the real device/pinout/clock, replace provisional constraints, and complete CDC, reset, I/O, and on-board timing validation. Numeric ownership is [../verification.md](../verification.md); physical handoff is [../hardware-handoff.md](../hardware-handoff.md).
