# Hardware handoff

This page lists the physical work that remains before any board-level claim. None of it is done in Phase 0.

## Pending physical work

1. Select FPGA device, package, board, voltage rails, I/O standards, and pinout.
2. Replace provisional LPF with legal board constraints and a real clock source.
3. Define source-synchronous trace/ETM electrical interface and polarity.
4. Validate DDR nibble capture across duty-cycle, skew, and voltage corners.
5. Validate asynchronous FIFO CDC, reset release, overflow stickiness, and recovery.
6. Connect and validate physical buffering/DDR if required by the board design.
7. Measure accepted counts, loss behavior, sustained capture, and replay acceptance on device.

## When boards arrive (order of operations)

Do these in order; do not skip ahead to rate metrics.

1. **Board contract** — freeze part number, package, rails, I/O standards, and every gateway pin; replace the clock-only LPF.
2. **Ingress electricals** — lock source-synchronous trace/ETM pinout, polarity, and sampling edge assumptions.
3. **DDR capture bench** — measure nibble alignment across duty cycle, skew, and voltage; record loss.
4. **CDC and reset** — run independent-clock stress on `async_fifo`; prove reset assertion/release and sticky overflow recovery in both domains.
5. **Buffering** — connect physical buffer/DDR if required; measure depth vs sustained accepted counts.
6. **Golden stream** — on-device round-trip of the 66-byte / 7-event DTRC golden with correct byte ordering.
7. **Replay acceptance** — hardware-sourced traces must satisfy the agreed 17-field comparison; only then write a timing/performance report (and only then consider bytes/sec).

This sequence matches [ROADMAP.md](ROADMAP.md) phases 1–6. Host `make demo` / `make evidence` results are not substitutes for any checkbox below.

## Signoff checklist

- [ ] Board and FPGA part number approved
- [ ] Package and every gateway pin assigned
- [ ] I/O standards, drive, slew, and termination reviewed
- [ ] Clock source, frequency, jitter, and duty cycle measured
- [ ] CDC review completed for `async_fifo`
- [ ] Reset assertion/release tested in both domains
- [ ] DDR rise/fall alignment measured at pins
- [ ] Overflow injection and sticky-status test passed
- [ ] Capture byte ordering compared with DTRC golden stream
- [ ] Physical buffer depth and sustained capture measured
- [ ] On-device 66-byte/7-event golden trace round-trips
- [ ] Hardware replay matches required 17-field acceptance criteria
- [ ] P&R warnings resolved or explicitly waived

## Boundary

The current P&R result is provisional, not physical validation: 111 TRELLIS_COMB, 93 TRELLIS_FF, 211.42 MHz provisional Fmax at 100 MHz, and 54 unconstrained-I/O warnings. No board timing, ETM correctness, or bytes/sec claim is signed off here.
