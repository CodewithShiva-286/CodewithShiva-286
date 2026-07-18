#!/usr/bin/env python3
"""Generate terminal-style project cards from data/projects.json."""

from __future__ import annotations

import argparse
import html
import os
import re

from scripts import _bootstrap  # noqa: F401
from scripts.paths import PROJECTS_JSON, PROJECTS_SVG, PROFILE_JSON
from scripts.svg_shell import fade_in_group, svg_close, svg_open, title_bar
from scripts.theme import THEME
from scripts.utils import load_json, write_text

W = 760
PAD = 22
TITLEBAR_H = 30
CARD_H = 110
CARD_GAP = 12
HEADER_H = 48


def repo_icon(x: float, y: float, *, size: float = 14) -> str:
    """Simple GitHub repo glyph."""
    return (
        f'<g transform="translate({x:.1f},{y:.1f})" fill="none" stroke="{THEME.muted}" stroke-width="1.2">'
        f'<path d="M0,{size * 0.35} C0,{size * 0.15} {size * 0.15},0 {size * 0.35},0 L{size * 0.85},0 '
        f'C{size},{0} {size},{size * 0.15} {size},{size * 0.35} L{size},{size * 0.85} '
        f'C{size},{size} {size * 0.85},{size} {size * 0.85},{size} L{size * 0.55},{size} L{size * 0.4},{size * 1.15} '
        f'L{size * 0.25},{size} L{size * 0.35},{size} C{size * 0.15},{size} 0,{size * 0.85} 0,{size * 0.65} Z"/>'
        f"</g>"
    )


def repo_placeholder(project: dict, profile: dict) -> str:
    """Return a stable repo placeholder when no repository URL is configured."""
    repo_url = str(project.get("repo_url", "")).strip()
    if repo_url:
        return repo_url

    username = profile["username"]
    slug = re.sub(r"[^a-z0-9]+", "-", project["name"].lower()).strip("-")
    return f"github.com/{username}/{slug}"


def render_card(project: dict, x: float, y: float, width: float) -> str:
    name = html.escape(project["name"])
    categories = html.escape(" · ".join(project["category"]))
    stack = html.escape(", ".join(project["stack"]))
    description = html.escape(project["description"])
    status = html.escape(project.get("status", "Active"))
    status_color = THEME.green if status.lower() == "active" else THEME.muted
    repo_url = html.escape(project["repo_display"])

    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{CARD_H}" rx="8" '
        f'fill="{THEME.bg2}" stroke="{THEME.frame}" stroke-opacity="0.8"/>'
        f'{repo_icon(x + 12, y + 12)}'
        f'<text x="{x + 32}" y="{y + 24}" fill="{THEME.green}" font-size="13" font-weight="700">{name}</text>'
        f'<text x="{x + width - 12}" y="{y + 24}" fill="{status_color}" font-size="11" '
        f'text-anchor="end">[{status}]</text>'
        f'<text x="{x + 12}" y="{y + 42}" fill="{THEME.section}" font-size="11">{categories}</text>'
        f'<text x="{x + 12}" y="{y + 58}" fill="{THEME.key}" font-size="11">stack:</text>'
        f'<text x="{x + 52}" y="{y + 58}" fill="{THEME.ink}" font-size="11">{stack}</text>'
        f'<text x="{x + 12}" y="{y + 76}" fill="{THEME.muted}" font-size="11">{description}</text>'
        f'<text x="{x + 12}" y="{y + 94}" fill="{THEME.key}" font-size="11">repo:</text>'
        f'<text x="{x + 48}" y="{y + 94}" fill="{THEME.ink}" font-size="11">{repo_url}</text>'
    )


def render_projects(projects: list[dict], profile: dict, *, static: bool = False) -> str:
    host = profile.get("host_label", profile["username"].lower())
    title = f"{host}@github: ~$ ls projects/"
    canvas_h = TITLEBAR_H + HEADER_H + len(projects) * (CARD_H + CARD_GAP) + PAD

    parts = svg_open(W, canvas_h)
    parts.extend(title_bar(W, title, pad=PAD, titlebar_h=TITLEBAR_H))
    parts.append(
        f'<text x="{PAD}" y="{TITLEBAR_H + 28}" fill="{THEME.muted}" font-size="12">'
        f"total {len(projects)} repositories listed</text>"
    )

    card_y = TITLEBAR_H + HEADER_H
    card_w = W - PAD * 2
    for index, project in enumerate(projects):
        card_project = dict(project)
        card_project["repo_display"] = repo_placeholder(project, profile)
        inner = render_card(card_project, PAD, card_y, card_w)
        parts.append(fade_in_group(inner, index, static=static, base_delay=0.08))
        card_y += CARD_H + CARD_GAP

    parts.extend(svg_close())
    return "".join(parts)


def generate_project_cards(out_path: str | None = None, *, static: bool | None = None) -> str:
    target = str(PROJECTS_SVG) if out_path is None else out_path
    profile = load_json(PROFILE_JSON)
    projects = load_json(PROJECTS_JSON)["projects"]
    is_static = bool(os.environ.get("STATIC")) if static is None else static
    write_text(target, render_projects(projects, profile, static=is_static))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate project cards SVG.")
    parser.add_argument("--out", default=str(PROJECTS_SVG))
    args = parser.parse_args()
    print(f"wrote {generate_project_cards(args.out)}")


if __name__ == "__main__":
    main()
