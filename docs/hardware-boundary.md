# Hardware boundary

The current host/RTL boundary is one ordered raw byte stream. RTL preserves byte order and does not interpret or package trace events; framing remains in the DTRC bytes produced by `Trace.encode()`.

Overflow and accepted count are sideband status, not packets in that stream. An overflowed capture is invalid and must not be decoded or replayed until the capture path is reset. Future host transport must surface both status values so callers can reject invalid captures and account for accepted bytes.

The checked-in FIFO simulation validates transport ordering and integrity only. It does not represent physical ETM capture, firmware timing, DDR, or clock-domain crossing behavior.
