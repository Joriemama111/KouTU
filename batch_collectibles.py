#!/usr/bin/env python3
"""
Batch process product photos: AI background removal + collectible-grade color grading.

Output: PNG with transparent background, brightened for catalog / collection display.
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance
from rembg import new_session, remove

DEFAULT_SUFFIX = "_collectible.png"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def collectible_grade(
    rgba: Image.Image,
    *,
    exposure: float = 1.28,
    lift: float = 22,
    contrast: float = 1.12,
    color: float = 1.18,
    sharpness: float = 1.2,
    warm_r: float = 1.02,
    cool_b: float = 0.98,
) -> Image.Image:
    """Brighten and polish RGB while preserving alpha."""
    r, g, b, a = rgba.split()
    rgb = Image.merge("RGB", (r, g, b))
    arr = np.array(rgb, dtype=np.float32)
    arr = arr * exposure + lift
    arr[:, :, 0] *= warm_r
    arr[:, :, 2] *= cool_b
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    rgb = Image.fromarray(arr)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Color(rgb).enhance(color)
    rgb = ImageEnhance.Sharpness(rgb).enhance(sharpness)
    r2, g2, b2 = rgb.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def process_one(
    src: Path,
    out: Path,
    session,
    *,
    skip_existing: bool,
    **grade_kwargs,
) -> str:
    if skip_existing and out.exists():
        return "skip"

    raw = src.read_bytes()
    cut = remove(raw, session=session)
    rgba = Image.open(io.BytesIO(cut)).convert("RGBA")
    final = collectible_grade(rgba, **grade_kwargs)
    out.parent.mkdir(parents=True, exist_ok=True)
    final.save(out, optimize=True)
    return "ok"


def iter_sources(src_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    files = [
        p
        for p in src_dir.glob(pattern)
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTS
        and "_cutout" not in p.stem
        and "_collectible" not in p.stem
        and "收藏品" not in p.stem
        and "抠图" not in p.stem
    ]
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove background and apply collectible-grade enhancement to product photos.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Input folder (or single image file)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output folder",
    )
    parser.add_argument(
        "--suffix",
        default=DEFAULT_SUFFIX,
        help=f"Output filename suffix (default: {DEFAULT_SUFFIX})",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Scan input folder recursively",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output files",
    )
    parser.add_argument(
        "--model",
        default="u2net",
        help="rembg model name (default: u2net)",
    )
    args = parser.parse_args()

    src = args.input.resolve()
    out_dir = args.output.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if src.is_file():
        sources = [src]
    elif src.is_dir():
        sources = iter_sources(src, args.recursive)
    else:
        print(f"Input not found: {src}", file=sys.stderr)
        return 1

    if not sources:
        print("No images found.", file=sys.stderr)
        return 1

    session = new_session(args.model)
    ok, skip, fail = 0, 0, 0
    total = len(sources)

    for i, path in enumerate(sources, 1):
        out = out_dir / f"{path.stem}{args.suffix}"
        try:
            status = process_one(
                path,
                out,
                session,
                skip_existing=not args.force,
            )
            if status == "skip":
                print(f"[{i}/{total}] skip {out.name}")
                skip += 1
            else:
                print(f"[{i}/{total}] ok {out.name}")
                ok += 1
        except Exception as e:
            print(f"[{i}/{total}] FAIL {path.name}: {e}", file=sys.stderr)
            fail += 1

    print(f"\nDone: {ok} ok, {skip} skipped, {fail} failed -> {out_dir}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
