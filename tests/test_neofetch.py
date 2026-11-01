"""
tests/test_neofetch.py:
Unit test suite verifying dot-leader row rendering, duration & pluralization,
number formatting, ASCII downsampling, heatmap metrics, and SVG XML validity.
"""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
import numpy as np
import pytest

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.build_card import render_row, build_terminal_card, build_contributions_card
from scripts.github_stats import compute_uptime, format_number
from scripts.make_ascii import ascii_from_image, ascii_from_text

def test_render_row_short_value():
    rows = render_row("GitHub", "frihk", width=52, min_dots=3)
    assert len(rows) == 1
    p, d, v = rows[0]
    full = p + d + v
    assert len(full) == 52
    assert p == ". GitHub: "
    assert v == " frihk"
    assert len(d) >= 3
    assert d.startswith("...")

def test_render_row_exact_fit():
    # Construct exact fit
    key = "TestKey"
    # prefix is ". TestKey: " (11 chars)
    # min_dots = 3, overhead = 11 + 3 + 1 = 15
    # available for value = 52 - 15 = 37
    val = "x" * 37
    rows = render_row(key, val, width=52, min_dots=3)
    assert len(rows) == 1
    p, d, v = rows[0]
    full = p + d + v
    assert len(full) == 52
    assert len(d) == 3

def test_render_row_overflow_wrap():
    long_value = "This is a very long string that should definitely wrap onto a secondary row in the neofetch card"
    rows = render_row("Program", long_value, width=52, min_dots=3)
    assert len(rows) >= 2
    # First row check
    p1, d1, v1 = rows[0]
    assert len(p1 + d1 + v1) == 52
    assert len(d1) >= 3
    # Second row check
    p2, d2, v2 = rows[1]
    assert len(p2 + d2 + v2) == 52

def test_compute_uptime_plurals():
    dt1 = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    # 1 year, 1 month, 1 day
    dt2 = datetime(2024, 2, 2, 0, 0, 0, tzinfo=timezone.utc)
    res = compute_uptime(dt1, dt2)
    assert res == "1 year, 1 month, 1 day"

    # 2 years, 3 months, 15 days
    dt3 = datetime(2025, 4, 16, 0, 0, 0, tzinfo=timezone.utc)
    res2 = compute_uptime(dt1, dt3)
    assert res2 == "2 years, 3 months, 15 days"

    # 0 years, 5 months, 2 days
    dt4 = datetime(2023, 6, 3, 0, 0, 0, tzinfo=timezone.utc)
    res3 = compute_uptime(dt1, dt4)
    assert res3 == "5 months, 2 days"

def test_format_number():
    assert format_number(0) == "0"
    assert format_number(95) == "95"
    assert format_number(2116) == "2,116"
    assert format_number(446276) == "446,276"

def test_ascii_mapper_synthetic_image():
    # Create 20x20 gradient image
    arr = np.linspace(0, 255, 20 * 20, dtype=np.uint8).reshape((20, 20))
    img = Image.fromarray(arr)
    ascii_res = ascii_from_image(img, columns=10, rows=5)
    lines = ascii_res.splitlines()
    assert len(lines) == 5
    assert len(lines[0]) == 10

def test_ascii_from_text_downsampler():
    dummy_text = "\n".join(["@@@@@@@@@@@@@@@@@@@@", "                    "] * 10)
    ascii_res = ascii_from_text(dummy_text, columns=10, rows=6)
    lines = ascii_res.splitlines()
    assert len(lines) == 6
    assert len(lines[0]) == 10

def test_svg_validity_and_cleanliness():
    stats = {
        "repos": 41,
        "contributed": 0,
        "stars": 0,
        "commits": 1513,
        "followers": 5,
        "first_commit": "2024-05-07",
        "member_since": "2023-08-14",
        "uptime": "2 years, 5 months, 25 days",
        "lines_of_code": {"total": 48210, "additions": 54120, "deletions": 5910},
        "contributions_last_year": 1513,
        "current_streak": 1,
        "longest_streak": 22,
        "calendar_weeks": [],
    }
    dummy_portrait = ["@" * 52] * 33

    for theme in ["dark", "light"]:
        card_svg = build_terminal_card(theme, stats, dummy_portrait)
        # Parse XML
        root = ET.fromstring(card_svg)
        assert root.tag.endswith("svg")
        # Ensure no invalid placeholders
        assert "{placeholder}" not in card_svg
        assert "None" not in card_svg
        assert "NaN" not in card_svg
        assert "undefined" not in card_svg

        contrib_svg = build_contributions_card(theme, stats)
        croot = ET.fromstring(contrib_svg)
        assert croot.tag.endswith("svg")
        assert "None" not in contrib_svg
