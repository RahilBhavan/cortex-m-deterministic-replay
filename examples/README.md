# Examples

| File | Meaning |
|---|---|
| `golden-demo.dtrc` | Encoded DTRC v2 stream from the seven-tag model demo (66 bytes) |
| `golden-demo.hex` | Same bytes as lowercase hex for inspection without binary tools |

The RTL tests use `golden-demo.dtrc` directly. When `$readmemh` is required, the test creates a temporary one-byte-per-line representation; the checked-in continuous `.hex` file remains the human-readable canonical comparison.

Regenerate with:

```sh
.venv/bin/python -c "from trace.format import Trace; t=Trace(events=[(1,2,3),(2,4,0x4000,7,1),(3,6,20,2,b'AB'),(4,8,9),(5,10,1),(6,12,0x1234),(7,14,0x55)]); open('examples/golden-demo.dtrc','wb').write(t.encode())"
```

These files are deterministic model-demo/transport goldens, not firmware workload data or hardware capture evidence. Real-ELF tests derive addresses, points, payloads, and expected register values from the built race ELF and live Unicorn state.
