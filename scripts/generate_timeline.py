#!/usr/bin/env python3
"""Generate a vertical terminal-style timeline SVG."""

from __future__ import annotations

import argparse
import html
import os

from scripts import _bootstrap  # noqa: F401
from scripts.paths import PROFILE_JSON, TIMELINE_JSON, TIMELINE_SVG
from scripts.svg_shell import fade_in_group, svg_close, svg_open, title_bar
from scripts.theme import THEME
from scripts.utils import load_json, write_text

W = 760
PAD = 28
TITLEBAR_H = 30
EVENT_H = 72


def render_timeline(events: list[dict], profile: dict, *, static: bool = False) -> str:
    host = profile.get("host_label", profile["username"].lower())
    title = f"{host}@github: ~$ git log --oneline"
    canvas_h = TITLEBAR_H + len(events) * EVENT_H + PAD + 20

    parts = svg_open(W, canvas_h)
    parts.extend(title_bar(W, title, pad=PAD, titlebar_h=TITLEBAR_H))

    x_line = PAD + 18
    y = TITLEBAR_H + 36

    for index, event in enumerate(events):
        is_last = index == len(events) - 1
        event_title = html.escape(event["title"])
        detail = html.escape(event.get("detail", ""))

        inner = (
            f'<circle cx="{x_line}" cy="{y}" r="5" fill="{THEME.green}"/>'
            f'<line x1="{x_line}" y1="{y + 6}" x2="{x_line}" y2="{y + EVENT_H - 18}" '
            f'stroke="{THEME.frame}" stroke-width="2" stroke-opacity="0.7"/>'
            f'<text x="{x_line + 20}" y="{y + 4}" fill="{THEME.green}" font-size="13" font-weight="700">'
            f"{event_title}</text>"
            f'<text x="{x_line + 20}" y="{y + 22}" fill="{THEME.muted}" font-size="11.5">{detail}</text>'
        )
        if not is_last:
            inner += (
                f'<text x="{x_line - 4}" y="{y + EVENT_H - 28}" fill="{THEME.accent}" '
                f'font-size="16" text-anchor="middle">&#8595;</text>'
            )

        parts.append(fade_in_group(inner, index, static=static, base_delay=0.1))
        y += EVENT_H

    parts.extend(svg_close())
    return "".join(parts)


def generate_timeline(out_path: str | None = None, *, static: bool | None = None) -> str:
    target = str(TIMELINE_SVG) if out_path is None else out_path
    profile = load_json(PROFILE_JSON)
    events = load_json(TIMELINE_JSON)["events"]
    is_static = bool(os.environ.get("STATIC")) if static is None else static
    write_text(target, render_timeline(events, profile, static=is_static))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate timeline SVG.")
    parser.add_argument("--out", default=str(TIMELINE_SVG))
    args = parser.parse_args()
    print(f"wrote {generate_timeline(args.out)}")


if __name__ == "__main__":
    main()
