---
name: koutu
description: >-
  Batch-remove backgrounds and apply collectible-grade color grading to flat-lay
  product photos (fridge magnets, enamel pins, badges). Uses rembg + PIL in this
  repo. Use when the user mentions 冰箱贴, 收藏品, 抠图, koutu, background removal for
  souvenirs, or catalog-style bright PNG exports.
---

# koutu

## Overview

This repo turns plain-background product photos into **transparent PNGs** with a **bright, catalog / collectible** look.

| Piece | Path |
|-------|------|
| Script | `batch_collectibles.py` (repo root) |
| Dependencies | `requirements.txt` |
| Details | `README.md` |

## Before running

1. Repo root = directory containing `batch_collectibles.py`.
2. Ensure venv + deps (once per machine):

```bash
cd <repo-root>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

First run downloads `u2net` (~176 MB) to `~/.u2net/`. Use `required_permissions: ["all"]` for long batches (writes outside workspace, model cache).

## Default workflow (user conventions)

When the user does not specify paths, infer from context or ask once:

| Role | Typical folder |
|------|----------------|
| Input | `…/单个冰箱贴/` or any folder of `.jpg` / `.jpeg` |
| Output | sibling `…/收藏品_单个冰箱贴/` |
| Suffix | `_收藏品.png` |

Skip files whose names already contain `抠图`, `收藏品`, `_cutout`, or `_collectible`.

## Commands

Always run via the project venv:

```bash
cd <repo-root>
source .venv/bin/activate

# Batch (most common)
python batch_collectibles.py \
  -i "<input-dir>" \
  -o "<output-dir>" \
  --suffix "_收藏品.png"

# Resume-friendly (default): existing outputs are skipped
# Re-process everything:
python batch_collectibles.py -i "<in>" -o "<out>" --suffix "_收藏品.png" --force

# One photo trial
python batch_collectibles.py -i "<one.jpg>" -o "<out-dir>" --suffix "_收藏品.png"

# Nested folders
python batch_collectibles.py -i "<in>" -o "<out>" -r --suffix "_收藏品.png"
```

For **79+ images**, run in background and monitor the log; expect several minutes on CPU.

## Agent checklist

1. Confirm input path exists and count images.
2. Create output directory if missing.
3. Run script with venv; do not duplicate pipeline logic in ad-hoc one-off scripts unless the user asks to change the algorithm.
4. Report: ok / skipped / failed counts and output folder path.
5. Optional: spot-check 1–2 PNGs (transparent background, brighter than source).

## Tuning

Collectible grading lives in `collectible_grade()` inside `batch_collectibles.py`. Change exposure / contrast / color only when the user says images are too dark, too flat, or oversaturated—keep alpha untouched.

## When NOT to use

- Multi-object scene photos needing per-item splits → not supported; use single-item flat lays.
- Video, RAW-only, or heavy retouch (liquify, inpaint) → out of scope.
- User only wants format conversion (HEIC→JPG) without cutout → use `sips` or similar, not this skill.
