#!/usr/bin/env python3
"""
Build a terminal-style information card from data/profile.json.

Technical profile only — no employer, role, or company fields.
"""

from __future__ import annotations

import argparse
import html
import os
from typing import Any

from scripts import _bootstrap  # noqa: F401
from scripts.paths import INFO_CARD_SVG, PROFILE_JSON
from scripts.svg_shell import fade_in_group, svg_close, svg_open, title_bar
from scripts.theme import THEME
from scripts.utils import load_json, write_text

W, H = 480, 430
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 118
LINE_H = 20.5


def _join(values: list[str]) -> str:
    return ", ".join(values)


def build_rows(profile: dict[str, Any]) -> list[tuple[str, ...]]:
    """Convert profile JSON into renderable row tuples."""
    host = profile.get("host_label", profile["username"].lower())
    rows: list[tuple[str, ...]] = [("host", host)]
    rows.append(("kv", "Name", profile["name"]))
    rows.append(("kv", "Education", profile["education"]))
    rows.append(("gap",))
    rows.append(("sec", "Domains"))
    rows.append(("val", _join(profile["domains"])))
    rows.append(("gap",))
    rows.append(("sec", "Programming Languages"))
    rows.append(("val", _join(profile["programming_languages"])))
    rows.append(("gap",))
    rows.append(("sec", "Frameworks"))
    rows.append(("val", _join(profile["frameworks"])))
    rows.append(("gap",))
    rows.append(("sec", "Technologies"))
    rows.append(("val", _join(profile["technologies"])))
    rows.append(("gap",))
    rows.append(("sec", "Cloud"))
    rows.append(("val", _join(profile["cloud"])))
    rows.append(("gap",))
    rows.append(("sec", "AI"))
    rows.append(("val", _join(profile["ai"])))
    return rows


def render_info_card(profile: dict[str, Any], *, static: bool = False) -> str:
    rows = build_rows(profile)
    host = profile.get("host_label", profile["username"].lower())
    title = f"{host}@github: ~$ neofetch"

    parts = svg_open(W, H)
    parts.extend(title_bar(W, title, pad=PAD, titlebar_h=TITLEBAR_H))

    y = TITLEBAR_H + 30
    anim_index = 0
    for row in rows:
        kind = row[0]
        if kind == "gap":
            y += LINE_H * 0.5
            continue

        inner = ""
        if kind == "host":
            label = html.escape(row[1])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                f'<tspan fill="{THEME.green}">{label}</tspan>'
                f'<tspan fill="{THEME.muted}">@</tspan>'
                f'<tspan fill="{THEME.accent}">github</tspan></text>'
                f'<line x1="{KEY_X + 96}" y1="{y - 4:.1f}" x2="{W - PAD}" y2="{y - 4:.1f}" '
                f'stroke="{THEME.frame}" stroke-opacity="0.8"/>'
            )
        elif kind == "sec":
            section = html.escape(row[1])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{THEME.section}" font-size="12.5" font-weight="700">'
                f"&#8212; {section}</text>"
                f'<line x1="{KEY_X + 12 + len(row[1]) * 8}" y1="{y - 4:.1f}" '
                f'x2="{W - PAD}" y2="{y - 4:.1f}" stroke="{THEME.frame}" stroke-opacity="0.8"/>'
            )
        elif kind == "kv":
            key, val = html.escape(row[1]), html.escape(row[2])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{THEME.key}" font-size="12.5" font-weight="700">{key}</text>'
                f'<text x="{VAL_X}" y="{y:.1f}" fill="{THEME.ink}" font-size="12.5">{val}</text>'
            )
        elif kind == "val":
            val = html.escape(row[1])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{THEME.ink}" font-size="12.5">{val}</text>'
            )

        if inner:
            parts.append(fade_in_group(inner, anim_index, static=static))
            anim_index += 1
            y += LINE_H

    parts.extend(svg_close())
    return "".join(parts)


def generate_info_card(out_path: str | None = None, *, static: bool | None = None) -> str:
    target = str(INFO_CARD_SVG) if out_path is None else out_path
    profile = load_json(PROFILE_JSON)
    is_static = bool(os.environ.get("STATIC")) if static is None else static
    svg = render_info_card(profile, static=is_static)
    write_text(target, svg)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate terminal info card SVG.")
    parser.add_argument("--out", default=str(INFO_CARD_SVG), help="Output SVG path")
    args = parser.parse_args()
    out = generate_info_card(args.out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
