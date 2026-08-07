# Demo assets

| File | Use |
|---|---|
| `make-demo.cast` | Asciinema v2 recording of `make demo` (`asciinema play make-demo.cast`) |
| `make-demo.gif` | Animated preview embedded from the README |

Regenerate after demo output changes:

```sh
.venv/bin/pip install pillow   # local asset tooling only; not a runtime dep
.venv/bin/python tools/record_demo_assets.py
```
