#!/usr/bin/env python3
"""Generate an animated terminal hero banner for the profile README."""

from __future__ import annotations

import argparse
import html
import os

from scripts import _bootstrap  # noqa: F401
from scripts.paths import HERO_SVG, PROFILE_JSON
from scripts.svg_shell import svg_close, svg_open, title_bar
from scripts.theme import THEME
from scripts.utils import load_json, write_text

W, H = 760, 180
PAD = 24
TITLEBAR_H = 30
LINE_H = 22


def render_hero(profile: dict, *, static: bool = False) -> str:
    host = profile.get("host_label", profile["username"].lower())
    lines = profile.get("hero", {}).get(
        "lines",
        ["$ ./init.sh", "> booting developer profile...", "> welcome."],
    )
    title = f"{host}@github: ~$ ./hero.sh"

    parts = svg_open(W, H)
    parts.extend(title_bar(W, title, pad=PAD, titlebar_h=TITLEBAR_H))

    y = TITLEBAR_H + 36
    for index, line in enumerate(lines):
        safe = html.escape(line)
        prefix = THEME.green if line.startswith("$") else THEME.muted
        text = (
            f'<text x="{PAD}" y="{y:.1f}" fill="{prefix}" font-size="14" font-weight="600">{safe}</text>'
        )
        if static:
            parts.append(text)
        else:
            delay = 0.2 + index * 0.35
            parts.append(
                f'<g opacity="0">{text}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.35s" fill="freeze"/></g>'
            )
        y += LINE_H

    cursor_y = y + 4
    parts.append(
        f'<text x="{PAD}" y="{cursor_y:.1f}" fill="{THEME.muted}" font-size="14">{host}@github:~$ </text>'
    )
    parts.append(
        f'<rect x="{PAD + 132}" y="{cursor_y - 13:.1f}" width="8" height="14" fill="{THEME.cursor}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )

    parts.extend(svg_close())
    return "".join(parts)


def generate_hero(out_path: str | None = None, *, static: bool | None = None) -> str:
    target = str(HERO_SVG) if out_path is None else out_path
    profile = load_json(PROFILE_JSON)
    is_static = bool(os.environ.get("STATIC")) if static is None else static
    write_text(target, render_hero(profile, static=is_static))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate hero banner SVG.")
    parser.add_argument("--out", default=str(HERO_SVG))
    args = parser.parse_args()
    print(f"wrote {generate_hero(args.out)}")


if __name__ == "__main__":
    main()
