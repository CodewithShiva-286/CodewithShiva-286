"""Small shared helpers for loading JSON and writing text files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    target = Path(path)
    with target.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
