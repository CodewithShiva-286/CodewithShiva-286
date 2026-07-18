#!/usr/bin/env python3
"""
Orchestrate the full GitHub profile asset pipeline.

Usage:
    python scripts/build.py
    python build.py
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from scripts import _bootstrap  # noqa: F401
from scripts.generate_ascii import generate_ascii
from scripts.generate_contribution_svg import generate_contribution_svg
from scripts.generate_hero import generate_hero
from scripts.generate_info_card import generate_info_card
from scripts.generate_project_cards import generate_project_cards
from scripts.generate_skill_tree import generate_skill_tree
from scripts.generate_timeline import generate_timeline
from scripts.paths import (
    ASCII_SVG,
    CONTRIBUTION_SVG,
    GENERATED,
    HERO_SVG,
    INFO_CARD_SVG,
    PROFILE_IMG,
    PROJECTS_SVG,
    ROOT,
    SKILLS_SVG,
    TIMELINE_SVG,
)
from scripts.prep_photo import prep_photo
from scripts.utils import load_json


def ensure_profile_image() -> None:
    """Copy fallback portrait asset to assets/profile.png if needed."""
    if PROFILE_IMG.exists():
        return
    fallback = ROOT / "assets" / "Untitled design.png"
    if fallback.exists():
        PROFILE_IMG.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fallback, PROFILE_IMG)
        print(f"copied {fallback.name} -> {PROFILE_IMG}")
    else:
        raise FileNotFoundError(
            f"Missing portrait at {PROFILE_IMG}. Add assets/profile.png and rerun."
        )


def fetch_contributions_safe(skip_fetch: bool) -> None:
    from scripts.paths import CONTRIBUTIONS_JSON

    if skip_fetch:
        if not CONTRIBUTIONS_JSON.exists():
            print("warning: --skip-fetch set but data/contributions.json is missing")
        return

    try:
        from scripts.fetch_contributions import fetch_contributions

        out = fetch_contributions()
        data = load_json(out)
        print(
            f"fetched contributions: {data['total_contributions']} total, "
            f"streak {data['current_streak']['length']}"
        )
    except Exception as exc:  # noqa: BLE001 — build should continue offline when possible
        if CONTRIBUTIONS_JSON.exists():
            print(f"warning: fetch failed ({exc}); using existing contributions.json")
        else:
            raise


def verify_outputs() -> None:
    """Fail fast if expected generated assets are missing or empty."""
    required_outputs = [
        HERO_SVG,
        ASCII_SVG,
        INFO_CARD_SVG,
        PROJECTS_SVG,
        SKILLS_SVG,
        TIMELINE_SVG,
        CONTRIBUTION_SVG,
    ]
    missing = [path for path in required_outputs if not path.exists()]
    if missing:
        missing_list = ", ".join(path.name for path in missing)
        raise FileNotFoundError(f"Missing generated assets: {missing_list}")

    empty = [path for path in required_outputs if path.stat().st_size == 0]
    if empty:
        empty_list = ", ".join(path.name for path in empty)
        raise ValueError(f"Generated empty assets: {empty_list}")

    print("verified generated outputs")


def build(*, skip_fetch: bool = False, static: bool = False) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    ensure_profile_image()

    print("==> prep_photo")
    prep_photo()

    print("==> generate_hero")
    generate_hero(static=static)

    print("==> generate_ascii")
    generate_ascii(static=static)

    print("==> generate_info_card")
    generate_info_card(static=static)

    print("==> generate_project_cards")
    generate_project_cards(static=static)

    print("==> generate_skill_tree")
    generate_skill_tree(static=static)

    print("==> generate_timeline")
    generate_timeline(static=static)

    print("==> fetch_contributions")
    fetch_contributions_safe(skip_fetch)

    print("==> generate_contribution_svg")
    generate_contribution_svg()

    print("==> verify_outputs")
    verify_outputs()

    print("done — generated assets in generated/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build all profile SVG assets.")
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip live GitHub fetch; reuse data/contributions.json",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Emit frozen SVGs without SMIL/CSS animations",
    )
    args = parser.parse_args()
    build(skip_fetch=args.skip_fetch, static=args.static)


if __name__ == "__main__":
    main()
