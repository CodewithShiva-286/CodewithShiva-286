#!/usr/bin/env python3
"""Root entrypoint — delegates to scripts/build.py."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from scripts.build import main

if __name__ == "__main__":
    main()
