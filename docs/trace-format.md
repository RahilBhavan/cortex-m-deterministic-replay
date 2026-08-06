# Trace format

DTRC v2: header magic/version/build ID, then tagged delta-count events. Tags 1 IRQ, 2 MMIO, 3 DMA, 4 external input, 5 race decision, 6 checkpoint, 7 optional state marker. CRC32 protects the complete body.

The host/RTL boundary is one byte stream: RTL captures and emits the exact bytes returned by `Trace.encode()` in byte order, without interpreting or re-framing event tags. Event framing remains in those DTRC bytes. The FIFO simulation is synthetic; it validates transport ordering and integrity, not physical ETM capture.
