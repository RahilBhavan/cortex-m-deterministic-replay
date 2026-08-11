# RTL results

## Observed tools and outputs

- Verilator 5.050 gateway simulations pass exact capture, overflow, and wrap behavior.
- Yosys 0.68+post `synth_ecp5` reports 41 LUT4, 93 FF, 2 EBR (`TRELLIS_DPR16X4`), and 22 CCU2C.
- nextpnr ECP5 `de8cd97`, Project Trellis 1.4_8, provisional `LFE5U-25F`/`CABGA381`: 111 TRELLIS_COMB and 93 TRELLIS_FF, 211.42 MHz provisional Fmax at 100 MHz, and 54 unconstrained-I/O warnings.

## Interpretation

The LPF constrains only the representative `clk` at 100 MHz. No pins or I/O standards are assigned. Therefore Fmax is a provisional tool estimate, not board timing; warnings are expected and must be resolved or waived during physical handoff.

The same-clock `gateway_top` synthesis does not prove the independent-clock behavior of `capture_gate`. CDC, reset, electrical ingress, buffering, and on-device capture remain pending. Numeric ownership is [verification.md](verification.md); physical acceptance is [hardware-handoff.md](hardware-handoff.md).
