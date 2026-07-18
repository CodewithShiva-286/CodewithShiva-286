#!/usr/bin/env python3
"""
Render data/contributions.json as an animated GitHub-style contribution heatmap SVG.

Self-hosted, no external stats services. Animation plays once on load then freezes.
"""

from __future__ import annotations

import argparse
import datetime
from typing import Any

from scripts import _bootstrap  # noqa: F401
from scripts.paths import CONTRIBUTION_SVG, CONTRIBUTIONS_JSON, PROFILE_JSON
from scripts.theme import CONTRIB_PALETTE, THEME
from scripts.utils import load_json, write_text

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

COL_T = 0.018
ROW_T = 0.045
CELL_DUR = 0.42


def level_for(count: int) -> int:
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(days: list[dict[str, Any]]) -> list[list[tuple[str, int, int] | None]]:
    first = datetime.date.fromisoformat(str(days[0]["date"]))
    lead_pad = (first.weekday() + 1) % 7
    grid: list[list[tuple[str, int, int] | None]] = []
    column: list[tuple[str, int, int] | None] = [None] * lead_pad

    for day in days:
        date = datetime.date.fromisoformat(str(day["date"]))
        weekday = (date.weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)
        column.append((str(day["date"]), int(day["count"]), level_for(int(day["count"]))))
        if len(column) == 7:
            grid.append(column)
            column = []

    if column:
        while len(column) < 7:
            column.append(None)
        grid.append(column)
    return grid


def render_contribution_svg(data: dict[str, Any], profile: dict[str, Any]) -> str:
    days = data["days"]
    grid = build_grid(days)
    n_cols = len(grid)
    art_w = n_cols * STEP
    art_h = 7 * STEP

    month_labels: list[tuple[int, str]] = []
    seen_months: set[tuple[int, int]] = set()
    for col_index, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((col_index, date.strftime("%b")))
            break

    canvas_w = PAD + LEFT_LABEL_W + art_w + PAD
    stats_h = 88
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD

    host = profile.get("host_label", profile["username"].lower())
    title = f"{host}@github: ~/contributions --graph"

    css = f"""
@keyframes cell {{
  0%   {{ opacity: 0; transform: translateY(-6px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
.c {{ opacity: 0; animation: cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both; }}
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f"<style>{css}</style>",
        "<defs>",
        f'<linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{THEME.bg2}"/><stop offset="1" stop-color="{THEME.bg}"/>'
        f"</linearGradient>",
        "</defs>",
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#hbg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w - 1}" height="{canvas_h - 1}" rx="12" '
        f'fill="none" stroke="{THEME.frame}" stroke-width="1" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" '
        f'stroke="{THEME.frame}" stroke-opacity="0.35"/>',
    ]

    for index, dotcol in enumerate(THEME.title_dots):
        parts.append(f'<circle cx="{PAD + index * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dotcol}"/>')
    parts.append(
        f'<text x="{canvas_w / 2}" y="{TITLEBAR_H / 2 + 4}" fill="{THEME.muted}" font-size="12" '
        f'text-anchor="middle">{title}</text>'
    )

    grid_top = TITLEBAR_H + TOP_LABEL_H
    grid_left = PAD + LEFT_LABEL_W

    for col_index, label in month_labels:
        x = grid_left + col_index * STEP
        parts.append(
            f'<text x="{x}" y="{TITLEBAR_H + 14}" fill="{THEME.muted}" font-size="10">{label}</text>'
        )

    for weekday_index, weekday_name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_top + weekday_index * STEP + CELL * 0.78
        parts.append(
            f'<text x="{PAD}" y="{y:.1f}" fill="{THEME.muted}" font-size="9">{weekday_name}</text>'
        )

    for col_index, column in enumerate(grid):
        gx = grid_left + col_index * STEP
        for row_index, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, level = cell
            gy = grid_top + row_index * STEP
            delay = col_index * COL_T + row_index * ROW_T
            plural = "s" if count != 1 else ""
            parts.append(
                f'<rect class="c" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{CONTRIB_PALETTE[level]}" style="animation-delay:{delay:.3f}s">'
                f"<title>{date_s}: {count} contribution{plural}</title></rect>"
            )

    leg_y = grid_top + art_h + 6
    leg_x = canvas_w - PAD - (len(CONTRIB_PALETTE) * (CELL - 1) + 70)
    parts.append(
        f'<text x="{leg_x}" y="{leg_y + CELL * 0.8:.1f}" fill="{THEME.muted}" font-size="10" text-anchor="end">Less</text>'
    )
    lx = leg_x + 8
    for color in CONTRIB_PALETTE:
        parts.append(
            f'<rect x="{lx}" y="{leg_y}" width="{CELL - 1}" height="{CELL - 1}" rx="2.2" fill="{color}"/>'
        )
        lx += CELL
    parts.append(
        f'<text x="{lx + 4}" y="{leg_y + CELL * 0.8:.1f}" fill="{THEME.muted}" font-size="10">More</text>'
    )

    sep_y = leg_y + CELL + 14
    parts.append(
        f'<line x1="0" y1="{sep_y}" x2="{canvas_w}" y2="{sep_y}" '
        f'stroke="{THEME.frame}" stroke-opacity="0.25"/>'
    )

    current_streak = data["current_streak"]["length"]
    longest_streak = data["longest_streak"]["length"]
    total = data["total_contributions"]
    best = data["best_day"]
    date_range = data["range"]

    line_y = sep_y + 24
    parts.append(
        f'<text x="{PAD}" y="{line_y}" font-size="13" fill="{THEME.green}">'
        f'<tspan font-weight="700">{total:,}</tspan>'
        f'<tspan fill="{THEME.muted}"> contributions in the last year</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_w - PAD}" y="{line_y}" font-size="12" fill="{THEME.muted}" text-anchor="end">'
        f'{date_range["start"]} &#8594; {date_range["end"]}</text>'
    )
    line_y += 24
    parts.append(
        f'<text x="{PAD}" y="{line_y}" font-size="13" fill="{THEME.muted}">current streak '
        f'<tspan fill="{THEME.accent}" font-weight="700">{current_streak} days</tspan>'
        f'<tspan fill="{THEME.muted}">   &#183;   longest </tspan>'
        f'<tspan fill="{THEME.accent}" font-weight="700">{longest_streak} days</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_w - PAD}" y="{line_y}" font-size="12" fill="{THEME.muted}" text-anchor="end">'
        f'best day <tspan fill="{THEME.green}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def generate_contribution_svg(
    in_path: str | None = None,
    out_path: str | None = None,
) -> str:
    source = str(CONTRIBUTIONS_JSON) if in_path is None else in_path
    target = str(CONTRIBUTION_SVG) if out_path is None else out_path
    data = load_json(source)
    profile = load_json(PROFILE_JSON)
    svg = render_contribution_svg(data, profile)
    write_text(target, svg)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate contribution heatmap SVG.")
    parser.add_argument("--in", dest="in_path", default=str(CONTRIBUTIONS_JSON))
    parser.add_argument("--out", default=str(CONTRIBUTION_SVG))
    args = parser.parse_args()
    out = generate_contribution_svg(args.in_path, args.out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
