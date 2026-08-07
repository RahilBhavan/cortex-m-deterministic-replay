# Documentation index

## System map

```mermaid
flowchart TB
 F[Firmware ELF] --> E[Unicorn CortexM]
 E --> C[Recorder]
 C --> W[DTRC v2 wire stream]
 W --> H[RTL capture gateway]
 W --> X[Replay]
 X --> Q[17-field snapshots]
 Q --> Z[Differ with disassembly]
```

| Page | Scope | Canonical facts |
|---|---|---|
| [architecture](architecture.md) | components and data flow | boundary ownership |
| [emulator-record-replay](emulator-record-replay.md) | algorithms and APIs | QEMU vs Unicorn; 17 fields |
| [trace-format](trace-format.md) | DTRC v2 wire contract | tags 1–7 and validation |
| [firmware-race](firmware-race.md) | commutation race | seeds and schedule |
| [rtl-gateway](rtl-gateway.md) | RTL/CDC design | capture paths and reset |
| [verification](verification.md) | measured numbers | commands and output |
| [runbooks](runbooks.md) | repeatable operations | troubleshooting |
| [demo-script](demo-script.md) | interview talk track | five-minute path |
| [resume-bullets](resume-bullets.md) | paste-ready claims | measured numbers only |
| [hardware-handoff](hardware-handoff.md) | pending physical work | signoff checklist |

Background: [scope](scope.md), [hardware boundary](hardware-boundary.md), [macOS setup](macos-setup.md), [QEMU investigation](qemu-instrumentation.md), [RTL results](rtl-results.md), [roadmap](ROADMAP.md), [journal](JOURNAL.md), [internal build prompt](internal/BUILD_PROMPT.md), and [ADRs](adr/001-emulation-host.md).
