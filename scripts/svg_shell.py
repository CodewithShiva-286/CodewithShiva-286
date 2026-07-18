"""Reusable terminal-window SVG chrome (title bar, frame, gradient background)."""

from __future__ import annotations

import html

from scripts.theme import FONT_STACK, THEME, Theme


def svg_open(width: int, height: int, *, theme: Theme = THEME) -> list[str]:
    """Return opening SVG tags including defs and background."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="{FONT_STACK}">',
        "<defs>",
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{theme.bg2}"/>'
        f'<stop offset="1" stop-color="{theme.bg}"/>'
        f"</linearGradient>",
        "</defs>",
        f'<rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" '
        f'fill="none" stroke="{theme.frame}" stroke-width="1" stroke-opacity="0.85"/>',
    ]


def title_bar(
    canvas_w: int,
    title: str,
    *,
    pad: int = 20,
    titlebar_h: int = 30,
    theme: Theme = THEME,
) -> list[str]:
    """Draw macOS-style dots and centered window title."""
    parts = [
        f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" '
        f'stroke="{theme.frame}" stroke-opacity="0.85"/>',
    ]
    for i, dotcol in enumerate(theme.title_dots):
        parts.append(
            f'<circle cx="{pad + i * 16}" cy="{titlebar_h / 2}" r="5" fill="{dotcol}"/>'
        )
    safe_title = html.escape(title)
    parts.append(
        f'<text x="{canvas_w / 2}" y="{titlebar_h / 2 + 4}" fill="{theme.muted}" '
        f'font-size="12" text-anchor="middle">{safe_title}</text>'
    )
    return parts


def svg_close() -> list[str]:
    return ["</svg>"]


def fade_in_group(inner: str, index: int, *, static: bool = False, base_delay: float = 0.12) -> str:
    """Staggered one-shot fade/slide animation for info rows."""
    if static:
        return f"<g>{inner}</g>"
    delay = base_delay + index * 0.06
    return (
        f'<g opacity="0" transform="translate(0,5)">{inner}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
        f'dur="0.4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" '
        f'keySplines="0.2 0.8 0.2 1"/></g>'
    )
