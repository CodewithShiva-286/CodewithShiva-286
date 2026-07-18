#!/usr/bin/env python3
"""
Prepare assets/profile.png for ASCII conversion.

Applies autocontrast, local contrast enhancement, and optional white-background
normalization so the portrait reads cleanly in a monochrome character ramp.
"""

from __future__ import annotations

import argparse

from PIL import Image, ImageEnhance, ImageOps

from scripts import _bootstrap  # noqa: F401
from scripts.paths import GENERATED, PROFILE_IMG, PREPPED_IMG

def prep_photo(
    src: str | None = None,
    dst: str | None = None,
    *,
    contrast: float = 1.35,
    brightness: float = 1.05,
    padding_ratio: float = 0.08,
) -> str:
    """Enhance portrait contrast, crop to subject bounds, and write grayscale PNG."""
    source = PROFILE_IMG if src is None else src
    target = PREPPED_IMG if dst is None else dst

    image = Image.open(source).convert("RGBA")
    gray = ImageOps.grayscale(image)

    # Crop to non-background content so the ASCII portrait fills the frame.
    mask = gray.point(lambda value: 255 if value < 245 else 0)
    bbox = mask.getbbox()
    if bbox:
        left, top, right, bottom = bbox
        width, height = gray.size
        pad_x = int((right - left) * padding_ratio)
        pad_y = int((bottom - top) * padding_ratio)
        left = max(0, left - pad_x)
        top = max(0, top - pad_y)
        right = min(width, right + pad_x)
        bottom = min(height, bottom + pad_y)
        gray = gray.crop((left, top, right, bottom))

    gray = ImageOps.autocontrast(gray, cutoff=2)
    gray = ImageEnhance.Brightness(gray).enhance(brightness)
    gray = ImageEnhance.Contrast(gray).enhance(contrast)

    out_path = str(target)
    gray.save(out_path, format="PNG")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare profile photo for ASCII art.")
    parser.add_argument("--src", default=str(PROFILE_IMG), help="Source portrait PNG")
    parser.add_argument("--dst", default=str(PREPPED_IMG), help="Output prepped PNG")
    args = parser.parse_args()

    GENERATED.mkdir(parents=True, exist_ok=True)
    out = prep_photo(args.src, args.dst)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
