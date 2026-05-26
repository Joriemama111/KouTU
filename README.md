# koutu

Batch process product photos (e.g. fridge magnets, enamel pins): **AI background removal** + **collectible-grade** color grading.

Designed for flat-lay photos on a plain background. Output is PNG with transparency, brightened for catalog or collection display.

## Features

- Background removal via [rembg](https://github.com/danielgatis/rembg) (U²-Net)
- Collectible look: exposure lift, mild warm tone, contrast / saturation / sharpness boost
- Batch folder or single file
- Skip existing outputs (resume-friendly)

## Requirements

- Python 3.10+
- macOS / Linux / Windows
- First run downloads the `u2net` model (~176 MB)

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Batch: input folder -> output folder
python batch_collectibles.py -i ./photos -o ./collectibles

# Recursive scan
python batch_collectibles.py -i ./photos -o ./collectibles -r

# Single file
python batch_collectibles.py -i ./one.jpg -o ./out

# Custom output suffix + overwrite
python batch_collectibles.py -i ./photos -o ./out --suffix "_收藏品.png" --force
```

## Output

- Format: PNG (RGBA, transparent background)
- Naming: `{original_stem}{suffix}` (default: `_collectible.png`)

## Pipeline

1. `rembg` removes background
2. `collectible_grade()` adjusts RGB only (alpha preserved):
   - Exposure ×1.28 + offset 22
   - Slight warm shift (R ×1.02, B ×0.98)
   - Contrast ×1.12, color ×1.18, sharpness ×1.2

Tune parameters in `collectible_grade()` if your lighting differs.

## Cursor Skill (koutu)

Included: `.cursor/skills/koutu/SKILL.md`

Clone this repo and open it as the Cursor workspace root (or copy the skill to your workspace `.cursor/skills/koutu/`).

In chat:「用 koutu 批量抠图做成收藏品」or mention 抠图 / 收藏品 / 冰箱贴.

## License

MIT
