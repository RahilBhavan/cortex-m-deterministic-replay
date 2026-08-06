# Roadmap

Prioritized remaining work:

1. Replace the synthetic model with real firmware/emulator race behavior and validate the contract against it.
2. Add 100k full-register validation across model and reference behavior.
3. Add 10k randomized codec cases, including malformed and boundary inputs.
4. Add disassembly-backed diagnostics for replay divergence.
5. Implement and validate DDR buffering and clock-domain-crossing capture paths, including surfaced overflow and accepted-count status.
6. Run ECP5 synthesis and measure Fmax; report results only when the toolchain and target constraints are available.
