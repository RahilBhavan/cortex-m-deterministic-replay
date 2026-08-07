#!/usr/bin/env python3
"""Regenerate docs/assets make-demo.cast and make-demo.gif from a live demo run."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"


def main() -> None:
    """Capture `tools.demo_race` stdout into cast + GIF assets."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [str(ROOT / ".venv/bin/python"), "-m", "tools.demo_race"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    all_lines = [
        "$ make demo",
        "make -C firmware",
        ".venv/bin/python -m tools.demo_race",
        *lines,
        "$",
    ]

    width, height = 88, 16
    header = {
        "version": 2,
        "width": width,
        "height": height,
        "timestamp": int(time.time()),
        "title": "make demo — Cortex-M deterministic race replay",
        "env": {"TERM": "xterm-256color", "SHELL": "/bin/zsh"},
    }
    t = 0.0
    events: list[list[object]] = []
    for line in all_lines:
        events.append([round(t, 3), "o", line + "\r\n"])
        t += 0.45 if line.startswith("$") else 0.35
    events.append([round(t + 1.2, 3), "o", ""])

    cast_path = ASSETS / "make-demo.cast"
    with cast_path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(header) + "\n")
        for event in events:
            handle.write(json.dumps(event) + "\n")

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    except OSError:
        font = ImageFont.load_default()

    char_w, char_h = 10, 20
    img_w = width * char_w + 24
    img_h = height * char_h + 24
    bg = (18, 18, 22)
    fg = (220, 220, 220)
    accent = (120, 200, 140)
    prompt = (120, 160, 255)

    frames: list[Image.Image] = []
    visible: list[str] = []
    for line in all_lines:
        visible.append(line)
        if len(visible) > height - 2:
            visible = visible[-(height - 2) :]
        img = Image.new("RGB", (img_w, img_h), bg)
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, img_w, 28), fill=(32, 32, 40))
        draw.text((12, 6), "make demo — DTRC Phase 0", fill=accent, font=font)
        y = 40
        for row in visible:
            color = prompt if row.startswith("$") else fg
            draw.text((12, y), row[: width - 2], fill=color, font=font)
            y += char_h
        frames.append(img)
    frames.extend([frames[-1]] * 8)

    gif_path = ASSETS / "make-demo.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=400,
        loop=0,
        optimize=True,
    )
    print(f"wrote {cast_path}")
    print(f"wrote {gif_path}")


if __name__ == "__main__":
    main()
