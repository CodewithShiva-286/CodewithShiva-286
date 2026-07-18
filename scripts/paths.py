"""Central path constants — keeps generators cross-platform and consistent."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"
GENERATED = ROOT / "generated"
ICONS = ASSETS / "icons"

PROFILE_IMG = ASSETS / "profile.png"
PREPPED_IMG = GENERATED / "profile-prepped.png"

PROFILE_JSON = DATA / "profile.json"
SKILLS_JSON = DATA / "skills.json"
PROJECTS_JSON = DATA / "projects.json"
TIMELINE_JSON = DATA / "timeline.json"
CONTRIBUTIONS_JSON = DATA / "contributions.json"

HERO_SVG = GENERATED / "hero.svg"
ASCII_SVG = GENERATED / "ascii.svg"
INFO_CARD_SVG = GENERATED / "info-card.svg"
CONTRIBUTION_SVG = GENERATED / "contribution.svg"
PROJECTS_SVG = GENERATED / "projects.svg"
SKILLS_SVG = GENERATED / "skills.svg"
TIMELINE_SVG = GENERATED / "timeline.svg"
