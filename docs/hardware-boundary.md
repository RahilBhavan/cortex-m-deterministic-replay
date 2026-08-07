# Hardware boundary

The host/RTL boundary is one ordered raw DTRC byte stream. DTRC semantics belong to [trace-format.md](trace-format.md); RTL transports bytes only. The measured demo is 66 bytes across 7 events, or 9.43 bytes/event. Bytes/sec is intentionally not reported because no emulated duration or clock contract exists.

`capture_fifo` is the same-clock reference FIFO used by direct Verilator tests. `capture_gate` models DDR nibble assembly followed by an asynchronous Gray-pointer FIFO; `gateway_top` ties both clocks together only for representative same-clock synthesis. These are different claims and must not be conflated.

Overflow and accepted count are sideband status. Overflow is sticky until coordinated reset and makes the capture invalid. Existing tests cover exact capture, overflow, and wrap; they do not validate physical ETM, pin timing, DDR, CDC metastability, board reset, sustained buffering, or silicon bandwidth.

Physical ownership and acceptance criteria are in [hardware-handoff.md](hardware-handoff.md). Numeric results belong in [verification.md](verification.md).
