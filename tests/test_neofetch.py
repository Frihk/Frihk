"""
tests/test_neofetch.py:
Unit test suite verifying dot-leader row rendering, duration & pluralization,
number formatting, ASCII downsampling, and SVG XML validity.
"""
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
import numpy as np
import pytest

import sys

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.build_card import (
    render_row,
    build_terminal_card,
    build_stats_card,
    build_top_langs_card,
)
from scripts.github_stats import compute_uptime, format_number, compute_top_languages
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
    key = "TestKey"
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
    p1, d1, v1 = rows[0]
    assert len(p1 + d1 + v1) == 52
    assert len(d1) >= 3
    p2, d2, v2 = rows[1]
    assert len(p2 + d2 + v2) == 52


def test_compute_uptime_plurals():
    dt1 = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    dt2 = datetime(2024, 2, 2, 0, 0, 0, tzinfo=timezone.utc)
    res = compute_uptime(dt1, dt2)
    assert res == "1 year, 1 month, 1 day"

    dt3 = datetime(2025, 4, 16, 0, 0, 0, tzinfo=timezone.utc)
    res2 = compute_uptime(dt1, dt3)
    assert res2 == "2 years, 3 months, 15 days"

    dt4 = datetime(2023, 6, 3, 0, 0, 0, tzinfo=timezone.utc)
    res3 = compute_uptime(dt1, dt4)
    assert res3 == "5 months, 2 days"


def test_format_number():
    assert format_number(0) == "0"
    assert format_number(95) == "95"
    assert format_number(2116) == "2,116"
    assert format_number(446276) == "446,276"


def test_compute_top_languages():
    langs = compute_top_languages({"Go": 600, "JavaScript": 300, "Python": 100, "ShaderLab": 500})
    assert [l["name"] for l in langs] == ["Go", "JavaScript", "Python"]
    assert langs[0]["percentage"] == 60.0


def test_ascii_mapper_synthetic_image():
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
        "prs": 30,
        "issues": 42,
        "followers": 5,
        "first_commit": "2024-05-07",
        "member_since": "2023-08-14",
        "uptime": "1 year",
        "top_languages": [
            {"name": "Go", "percentage": 38.87},
            {"name": "JavaScript", "percentage": 25.13},
            {"name": "Python", "percentage": 19.15},
            {"name": "TypeScript", "percentage": 8.79},
            {"name": "CSS", "percentage": 5.12},
            {"name": "HTML", "percentage": 2.94},
        ],
    }
    dummy_portrait = ["@" * 52] * 33

    for theme in ["dark", "light"]:
        card_svg = build_terminal_card(theme, stats, dummy_portrait)
        root = ET.fromstring(card_svg)
        assert root.tag.endswith("svg")
        assert "Software developer" in card_svg
        assert "1 year" in card_svg
        assert "English, Swahili" in card_svg
        assert "ian kimani" in card_svg
        assert "frihkian05@gmail.com" not in card_svg

        stats_svg = build_stats_card(theme, stats)
        sroot = ET.fromstring(stats_svg)
        assert sroot.tag.endswith("svg")
        assert "1,513" in stats_svg

        langs_svg = build_top_langs_card(theme, stats)
        lroot = ET.fromstring(langs_svg)
        assert lroot.tag.endswith("svg")
        assert "Go" in langs_svg
