#!/usr/bin/env python3
"""Generate a terminal-style categorized skill tree SVG."""

from __future__ import annotations

import argparse
import html
import os

from scripts import _bootstrap  # noqa: F401
from scripts.paths import PROFILE_JSON, SKILLS_JSON, SKILLS_SVG
from scripts.svg_shell import fade_in_group, svg_close, svg_open, title_bar
from scripts.theme import THEME
from scripts.utils import load_json, write_text

W = 760
PAD = 22
TITLEBAR_H = 30
COL_W = (W - PAD * 2 - 16) / 2
LINE_H = 18
SECTION_GAP = 10


def render_category(name: str, skills: list[str], x: float, y: float) -> tuple[str, float]:
    parts = [
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{THEME.section}" font-size="12" font-weight="700">'
        f"## {html.escape(name)}</text>"
    ]
    y += LINE_H
    for skill in skills:
        parts.append(
            f'<text x="{x + 8:.1f}" y="{y:.1f}" fill="{THEME.ink}" font-size="11.5">'
            f'<tspan fill="{THEME.green}">></tspan> {html.escape(skill)}</text>'
        )
        y += LINE_H
    y += SECTION_GAP
    return "".join(parts), y


def render_skills(categories: list[dict], profile: dict, *, static: bool = False) -> str:
    host = profile.get("host_label", profile["username"].lower())
    title = f"{host}@github: ~$ cat skills.txt"

    # Two-column layout: estimate height from left column stack.
    left_categories = categories[::2]
    right_categories = categories[1::2]

    def column_height(items: list[dict]) -> float:
        height = 0.0
        for item in items:
            height += LINE_H + len(item["skills"]) * LINE_H + SECTION_GAP
        return height

    content_h = max(column_height(left_categories), column_height(right_categories)) + 24
    canvas_h = TITLEBAR_H + content_h + PAD

    parts = svg_open(W, canvas_h)
    parts.extend(title_bar(W, title, pad=PAD, titlebar_h=TITLEBAR_H))

    left_x = PAD
    right_x = PAD + COL_W + 16
    top_y = TITLEBAR_H + 28

    anim_index = 0
    y_left = top_y
    for category in left_categories:
        inner, y_left = render_category(category["name"], category["skills"], left_x, y_left)
        parts.append(fade_in_group(inner, anim_index, static=static, base_delay=0.06))
        anim_index += 1

    y_right = top_y
    for category in right_categories:
        inner, y_right = render_category(category["name"], category["skills"], right_x, y_right)
        parts.append(fade_in_group(inner, anim_index, static=static, base_delay=0.06))
        anim_index += 1

    parts.extend(svg_close())
    return "".join(parts)


def generate_skill_tree(out_path: str | None = None, *, static: bool | None = None) -> str:
    target = str(SKILLS_SVG) if out_path is None else out_path
    profile = load_json(PROFILE_JSON)
    categories = load_json(SKILLS_JSON)["categories"]
    is_static = bool(os.environ.get("STATIC")) if static is None else static
    write_text(target, render_skills(categories, profile, static=is_static))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate skill tree SVG.")
    parser.add_argument("--out", default=str(SKILLS_SVG))
    args = parser.parse_args()
    print(f"wrote {generate_skill_tree(args.out)}")


if __name__ == "__main__":
    main()
