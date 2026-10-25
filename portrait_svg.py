#!/usr/bin/env python3
"""
portrait_svg.py:
Adjusts portrait.svg aspect ratio and scanline bounds to perfectly match
the bio text height in the two-column hero table while preserving ASCII art positioning.
"""
import re
import sys

def adjust_portrait_aspect_ratio(svg_path, target_height=1300):
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg = f.read()

    # 1. Update <svg ... width="880" height="870" viewBox="0 0 880 870">
    svg = re.sub(
        r'height="[\d\.]+"\s+viewBox="0\s+0\s+880\s+[\d\.]+"',
        f'height="{target_height}" viewBox="0 0 880 {target_height}"',
        svg
    )

    # 2. Update background outer border:
    # <rect x="0.5" y="0.5" width="879" height="869" rx="12" ... />
    svg = re.sub(
        r'<rect\s+x="0\.5"\s+y="0\.5"\s+width="879"\s+height="[\d\.]+"\s+rx="12"',
        f'<rect x="0.5" y="0.5" width="879" height="{target_height - 1}" rx="12"',
        svg
    )

    # 3. Update scanlines rect:
    # <rect x="1" y="41" width="878" height="828" rx="11" fill="url(#sc)" pointer-events="none"/>
    svg = re.sub(
        r'<rect\s+x="1"\s+y="41"\s+width="878"\s+height="[\d\.]+"\s+rx="11"\s+fill="url\(#sc\)"',
        f'<rect x="1" y="41" width="878" height="{target_height - 42}" rx="11" fill="url(#sc)"',
        svg
    )

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Updated {svg_path} to height={target_height}, viewBox='0 0 880 {target_height}'")

if __name__ == '__main__':
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 1300
    adjust_portrait_aspect_ratio('portrait.svg', target)
