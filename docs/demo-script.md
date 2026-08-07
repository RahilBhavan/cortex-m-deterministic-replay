# Five-minute demo script

Use this talk track in interviews. Run from a built tree with `.venv` installed.

## 1. Problem (30s)

Embedded races are nondeterministic. Wall-clock debugging does not reproduce them. Deterministic replay needs every source of nondeterminism recorded at instruction-count granularity: interrupts, MMIO reads, and DMA writes.

## 2. Race rarity (60s)

```sh
make demo
```

Expect seed 0 → `corruptions=2` per 1,000 trials, then one corrupting schedule replayed bit-identically. Mention seeds 1–3 are `1/2/1` in [verification.md](verification.md). Preview: [assets/make-demo.gif](assets/make-demo.gif).

## 3. Bit-identical replay (60s)

Point at the demo’s Unicorn record/replay identity line. Optionally expand:

```sh
.venv/bin/python -m unittest tests.test_race_replay -v
.venv/bin/python -m unittest tests.test_replay.ReplayTest.test_record_replay_identity -v
```

Claim: 17 fields (R0–R12, SP, LR, PC, xPSR); campaign evidence is 100,000/100,000.

## 4. Differ / first divergence (60s)

```sh
.venv/bin/python -m unittest tests.test_differ -v
```

Show that altering an MMIO value localizes the first mismatched snapshot and can attach disassembly.

## 5. RTL capture gate (60s)

If Verilator is available:

```sh
make gateway-test
```

Explain: bytes only, sticky overflow invalidates the stream, `gateway_top` same-clock synth is provisional, pinout unfinished.

## 6. Honest handoff (30s)

Open [hardware-handoff.md](hardware-handoff.md). All signoff boxes are unchecked. Next physical step is board/part/pin selection, not inventing bytes/sec from the host demo.
