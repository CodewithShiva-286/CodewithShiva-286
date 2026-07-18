#!/usr/bin/env python3
"""
Convert a prepped portrait into a monochrome ASCII-art SVG with a one-shot
row-by-row typing animation and blinking cursor (SMIL, no JavaScript).
"""

from __future__ import annotations

import argparse
import html
import os

from PIL import Image, ImageEnhance

from scripts import _bootstrap  # noqa: F401
from scripts.paths import ASCII_SVG, PREPPED_IMG, PROFILE_JSON
from scripts.svg_shell import svg_close, svg_open, title_bar
from scripts.theme import THEME
from scripts.utils import load_json, write_text

# Grid density — tuned for a premium, low-noise portrait.
COLS = 100
ROWS = 53
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"

CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.18
WHITE_FLOOR = 0.80

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H

ROW_DUR = 0.11
STAGGER = 0.11


def sample_ascii_rows(src_path: str) -> list[str]:
    """Map image luminance to monospace character rows."""
    image = Image.open(src_path).convert("L")
    image = ImageEnhance.Brightness(image).enhance(BRIGHTNESS)
    image = ImageEnhance.Contrast(image).enhance(CONTRAST)
    image = image.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    pixels = image.load()

    rows: list[str] = []
    for y in range(ROWS):
        chars: list[str] = []
        for x in range(COLS):
            lum = pixels[x, y] / 255.0
            lum = pow(lum, GAMMA)
            if lum >= WHITE_FLOOR:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            idx = max(0, min(len(RAMP) - 1, idx))
            chars.append(RAMP[idx])
        rows.append("".join(chars))
    return rows


def render_ascii_svg(rows: list[str], profile: dict, *, static: bool = False) -> str:
    """Build animated ASCII portrait SVG."""
    canvas_w = ART_W + PAD * 2
    canvas_h = TITLEBAR_H + ART_H + STATUS_H + PAD
    host = profile.get("host_label", profile["username"].lower())
    name = profile["name"]
    title = f"{host}@github: ~$ ./portrait.sh"

    parts = svg_open(canvas_w, canvas_h)
    parts.extend(title_bar(canvas_w, title, pad=PAD, titlebar_h=TITLEBAR_H))

    art_top = TITLEBAR_H + PAD * 0.35
    font_size = CELL_H * 0.86

    for row_index, line in enumerate(rows):
        y = art_top + row_index * CELL_H + CELL_H * 0.74
        row_y = art_top + row_index * CELL_H
        delay = row_index * STAGGER
        safe = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{THEME.ink}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>'
        )

        if static:
            parts.append(text)
            continue

        parts.append(
            f'<clipPath id="r{row_index}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{row_index})">{text}</g>')
        parts.append(
            f'<rect y="{row_y + 1:.1f}" width="{CELL_W}" height="{CELL_H - 2}" '
            f'fill="{THEME.cursor}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay + ROW_DUR:.3f}s"/></rect>'
        )

    status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
    status_y = status_line_y + 19
    parts.append(
        f'<line x1="0" y1="{status_line_y:.1f}" x2="{canvas_w}" y2="{status_line_y:.1f}" '
        f'stroke="{THEME.frame}"/>'
    )
    parts.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{THEME.muted}" font-size="13">'
        f'{host}@github:~$ whoami <tspan fill="{THEME.ink}">{html.escape(name)}</tspan></text>'
    )
    cursor_x = PAD + 196
    parts.append(
        f'<rect x="{cursor_x}" y="{status_y - 12:.1f}" width="8" height="14" fill="{THEME.cursor}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )

    parts.extend(svg_close())
    return "".join(parts)


def generate_ascii(
    src_path: str | None = None,
    out_path: str | None = None,
    *,
    static: bool | None = None,
) -> str:
    """Generate ASCII SVG from prepped portrait and profile metadata."""
    source = str(PREPPED_IMG) if src_path is None else src_path
    target = str(ASCII_SVG) if out_path is None else out_path
    profile = load_json(PROFILE_JSON)
    is_static = bool(os.environ.get("STATIC")) if static is None else static

    rows = sample_ascii_rows(source)
    svg = render_ascii_svg(rows, profile, static=is_static)
    write_text(target, svg)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ASCII portrait SVG.")
    parser.add_argument("--src", default=str(PREPPED_IMG), help="Prepped portrait PNG")
    parser.add_argument("--out", default=str(ASCII_SVG), help="Output SVG path")
    args = parser.parse_args()

    out = generate_ascii(args.src, args.out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
