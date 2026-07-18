"""Shared terminal theme constants for all SVG generators."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Monochrome cyber-terminal palette with subtle green accents."""

    bg: str = "#0a0e14"
    bg2: str = "#0d1117"
    frame: str = "#30363d"
    muted: str = "#7d8590"
    text: str = "#c9d1d9"
    green: str = "#3fb950"
    accent: str = "#39d353"
    key: str = "#7ee787"
    section: str = "#56d364"
    cursor: str = "#c9d1d9"
    ink: str = "#c9d1d9"
    title_dots: tuple[str, str, str] = ("#ff5f56", "#ffbd2e", "#27c93f")


THEME = Theme()

# GitHub-style contribution ramp — green only, no neon flash.
CONTRIB_PALETTE: list[str] = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

FONT_STACK = (
    "ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace"
)
