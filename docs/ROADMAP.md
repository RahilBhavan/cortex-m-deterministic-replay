# Roadmap

The host-side prototype is complete for its stated scope. Remaining work is physical validation, not another emulator fallback.

| Phase | Deliverable | Exit evidence |
|---|---|---|
| 1 | board/device/package/pinout and I/O contract | approved schematic, LPF, clock plan |
| 2 | physical trace/ETM ingress and DDR capture | pin-level waveform and loss tests |
| 3 | CDC/reset/buffering validation | independent-clock stress, reset recovery, overflow logs |
| 4 | on-device golden stream | exact 66-byte DTRC round trip |
| 5 | physical replay acceptance | agreed 17-field comparison and reproducible race |
| 6 | timing/performance report | measured clock, accepted counts, sustained capture; only then consider rate metrics |

Do not convert provisional P&R into hardware timing, or stream size into bytes/sec. See [hardware-handoff.md](hardware-handoff.md).
