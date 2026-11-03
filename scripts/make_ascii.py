#!/usr/bin/env python3
"""
scripts/make_ascii.py:
Deterministic generator for ASCII-art portraits.
Supports both image inputs (PNG, JPG, etc.) and text ASCII downsampling.
Calibrated for monospace font aspect ratios (~0.5 width/height).
"""
import argparse
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
import numpy as np

# Default ramp from sparse to dense
DEFAULT_RAMP = " .,:;-=+*#%@"

# Character densities used for parsing existing ASCII art
CHAR_DENSITY_MAP = {
    ' ': 0.0,
    '.': 0.12, ',': 0.12, "'": 0.12, '`': 0.12, '^': 0.12, '-': 0.12,
    ':': 0.25, ';': 0.25, '~': 0.25, '_': 0.25,
    '!': 0.40, '(': 0.40, ')': 0.40, '[': 0.40, ']': 0.40, '/': 0.40, '\\': 0.40, '|': 0.40, '<': 0.40, '>': 0.40, '?': 0.40,
    '=': 0.55, '+': 0.55, '*': 0.55,
    'c': 0.68, 'l': 0.68, 's': 0.68, 'z': 0.68, 'u': 0.68, 'v': 0.68, 'w': 0.68,
    'C': 0.78, 'E': 0.78, 'F': 0.78, 'G': 0.78, 'J': 0.78, 'L': 0.78, 'S': 0.78, 'Z': 0.78, '2': 0.78, '3': 0.78, '7': 0.78,
    '%': 0.90, '#': 0.90,
    '@': 1.0,
}

def ascii_from_image(
    image: Image.Image,
    columns: int = 52,
    rows: int = 34,
    contrast: float = 1.3,
    gamma: float = 1.1,
    ramp: str = DEFAULT_RAMP,
) -> str:
    """Convert a PIL Image to an ASCII string grid."""
    gray = ImageOps.grayscale(image)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(contrast)

    # Resize to columns x rows
    resized = gray.resize((columns, rows), Image.Resampling.LANCZOS)
    arr = np.array(resized, dtype=np.float32) / 255.0

    if gamma != 1.0:
        arr = np.clip(arr ** gamma, 0.0, 1.0)

    ramp_len = len(ramp)
    lines = []
    for row in arr:
        line = "".join(ramp[min(int(val * ramp_len), ramp_len - 1)] for val in row)
        lines.append(line)
    return "\n".join(lines)

def ascii_from_text(
    text: str,
    columns: int = 52,
    rows: int = 34,
    contrast: float = 1.3,
    gamma: float = 1.2,
    ramp: str = DEFAULT_RAMP,
) -> str:
    """Downsample existing high-resolution ASCII art to target columns x rows."""
    raw_lines = [line.rstrip("\r\n") for line in text.splitlines() if line]
    if not raw_lines:
        return ""
    max_len = max(len(l) for l in raw_lines)
    padded = [l.ljust(max_len) for l in raw_lines]

    grid = np.zeros((len(padded), max_len), dtype=np.float32)
    for r, line in enumerate(padded):
        for c, ch in enumerate(line):
            grid[r, c] = CHAR_DENSITY_MAP.get(ch, 0.5 if ch.strip() else 0.0)

    # Convert to PIL Image for high-quality resampling
    img = Image.fromarray((grid * 255).astype(np.uint8))
    resized = img.resize((columns, rows), Image.Resampling.LANCZOS)
    arr = np.array(resized, dtype=np.float32) / 255.0

    if contrast != 1.0:
        arr = np.clip(arr * contrast, 0.0, 1.0)
    if gamma != 1.0:
        arr = np.clip(arr ** gamma, 0.0, 1.0)

    ramp_len = len(ramp)
    lines = []
    for row in arr:
        line = "".join(ramp[min(int(val * ramp_len), ramp_len - 1)] for val in row)
        lines.append(line)
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Generate deterministic ASCII portrait for neofetch terminal card."
    )
    parser.add_argument("--source", type=str, help="Path to input image file (PNG/JPG)")
    parser.add_argument("--text-source", type=str, default="assets/portrait.txt", help="Path to existing ASCII text file")
    parser.add_argument("--output", type=str, default="assets/portrait.txt", help="Path to output text file")
    parser.add_argument("--columns", type=int, default=52, help="Output columns (width in characters)")
    parser.add_argument("--rows", type=int, default=34, help="Output rows (height in lines)")
    parser.add_argument("--contrast", type=float, default=1.3, help="Contrast adjustment factor")
    parser.add_argument("--gamma", type=float, default=1.2, help="Gamma exponent")
    parser.add_argument("--ramp", type=str, default=DEFAULT_RAMP, help="Character ramp from dark to bright")

    args = parser.parse_args()

    if args.source and Path(args.source).exists():
        img = Image.open(args.source)
        result = ascii_from_image(
            img,
            columns=args.columns,
            rows=args.rows,
            contrast=args.contrast,
            gamma=args.gamma,
            ramp=args.ramp,
        )
    elif args.text_source and Path(args.text_source).exists():
        with open(args.text_source, "r", encoding="utf-8") as f:
            raw_text = f.read()
        result = ascii_from_text(
            raw_text,
            columns=args.columns,
            rows=args.rows,
            contrast=args.contrast,
            gamma=args.gamma,
            ramp=args.ramp,
        )
    else:
        print(f"Error: Neither source image nor text source found.", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding="utf-8")

    lines = result.splitlines()
    print(f"ASCII portrait written to {out_path} ({len(lines[0]) if lines else 0} cols × {len(lines)} rows)")

if __name__ == "__main__":
    main()
