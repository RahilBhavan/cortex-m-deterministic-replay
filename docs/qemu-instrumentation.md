# QEMU instrumentation investigation

QEMU is retained only for boot smoke. The exact recorder uses Unicorn because the required controls are absent from the available QEMU interfaces.

The plausible execution point is `accel/tcg/cpu-exec.c:431` (`cpu_tb_exec`), but it is translated-block execution, not a stable post-retirement callback. The plugin instruction notification is execution-only. MMIO callbacks report accesses after the operation and cannot return a replacement read value. External IRQ APIs schedule a level, not an instruction-count event.

Exact support would require coordinated changes to TCG retirement boundaries, plugin/API state plumbing, ARM MMIO load paths, and the M-profile interrupt scheduler. This is why no QEMU patch is vendored and no QEMU race/replay number is claimed.

```sh
qemu-system-arm --version
make -C firmware smoke
```

The gate is intentionally conservative: QEMU boots the real image, while Unicorn 2.1.4 supplies deterministic one-instruction execution and a narrow exception shim. See [adr/001-emulation-host.md](adr/001-emulation-host.md).
