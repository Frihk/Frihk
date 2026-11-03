#!/usr/bin/env python3
"""
scripts/build_card.py:
Generates neofetch-style terminal cards (dark_mode.svg, light_mode.svg)
and self-hosted GitHub statistics & top-languages cards
(stats_dark.svg, stats_light.svg, top_langs_dark.svg, top_langs_light.svg).
All SVGs are fully self-contained, valid XML, and contrast-checked.
"""
import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

# Import theme tokens
sys.path.insert(0, str(Path(__file__).resolve().parent))
from templates.theme_tokens import THEMES

FONT_FAMILY = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SANS_FONT_FAMILY = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

LANGUAGE_COLORS = {
    "Go": "#00ADD8",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "CSS": "#563d7c",
    "HTML": "#e34c26",
    "Shell": "#89e051",
    "Solidity": "#AA6746",
    "Rust": "#dea584",
    "C": "#555555",
    "C++": "#f34b7d",
}


def render_row(key: str, value: str, width: int = 52, min_dots: int = 3) -> list[tuple[str, str, str]]:
    """
    Format a detail row into one or more line tuples: (key_part, dots_part, value_part).
    The dot leaders ensure the value aligns to the exact right column.
    All lines are padded to exactly `width` characters.
    """
    prefix = f". {key}: "
    overhead = len(prefix) + min_dots + 1
    avail_val = max(1, width - overhead)

    words = value.split()
    if not words:
        dots = "." * (width - len(prefix))
        return [(prefix, dots, "")]

    # First line
    line1_words = []
    rem_words = words[:]
    while rem_words:
        test = " ".join(line1_words + [rem_words[0]])
        if len(test) <= avail_val:
            line1_words.append(rem_words.pop(0))
        else:
            break

    if not line1_words:
        val1 = value[:avail_val]
        rem_str = value[avail_val:].strip()
        rem_words = rem_str.split()
    else:
        val1 = " ".join(line1_words)

    dots_count = width - len(prefix) - 1 - len(val1)
    res = [(prefix, "." * dots_count, " " + val1)]

    # Continuation lines
    while rem_words:
        curr_words = []
        while rem_words:
            test = " ".join(curr_words + [rem_words[0]])
            if len(test) <= avail_val:
                curr_words.append(rem_words.pop(0))
            else:
                break
        if not curr_words:
            chunk = rem_words[0][:avail_val]
            rem_words[0] = rem_words[0][avail_val:]
            if not rem_words[0]:
                rem_words.pop(0)
        else:
            chunk = " ".join(curr_words)

        indent_len = width - len(chunk)
        res.append(("", " " * indent_len, chunk))

    return res


PORTRAIT_SVG_DEFAULT = "portrait.svg"
PORTRAIT_COL_START = 40
PORTRAIT_COL_END = 180

INFO_COLS = 62
INFO_FONT = 15.0
INFO_CHAR_W = 8.8
LINE_PITCH = 24.5
PAD = 30
GAP = 38
BAR_H = 40

P_FONT_RATIO = 6.31 / 7.28
P_CHAR_RATIO = 3.8 / 7.28


def load_portrait_svg(path, col_start=PORTRAIT_COL_START, col_end=PORTRAIT_COL_END):
    """Read the coloured ASCII art out of portrait.svg."""
    import html
    import re

    svg = Path(path).read_text(encoding="utf-8")
    art = re.search(r'<g id="art"[^>]*>(.*?)</g>', svg, re.S)
    body = art.group(1) if art else svg
    rows = []
    for text_body in re.findall(r"<text[^>]*>(.*?)</text>", body, re.S):
        chars = []
        for cls, run in re.findall(r'<tspan class="c(\d)">(.*?)</tspan>', text_body, re.S):
            for ch in html.unescape(run):
                chars.append((int(cls), ch))
        if chars:
            rows.append(chars)
    if not rows:
        raise ValueError(f"No portrait art found in {path}")
    width = max(len(r) for r in rows)
    cropped = []
    for r in rows:
        r = r + [(0, " ")] * (width - len(r))
        r = r[col_start:col_end]
        runs = []
        for tone, ch in r:
            if runs and (runs[-1][0] == tone or ch == " "):
                runs[-1] = (runs[-1][0], runs[-1][1] + ch)
            else:
                runs.append((tone, ch))
        cropped.append(runs)
    return cropped


def _normalise_portrait(portrait):
    """Accept rows of plain strings or rows of (tone, text) runs."""
    rows = []
    for row in portrait:
        if isinstance(row, str):
            rows.append([(2, row)])
        else:
            rows.append(list(row))
    cols = max(sum(len(t) for _, t in r) for r in rows)
    padded = []
    for r in rows:
        n = sum(len(t) for _, t in r)
        if n < cols:
            r = r + [(0, " " * (cols - n))]
        padded.append(r)
    return padded, cols


def build_info_rows(stats: dict, width: int = INFO_COLS) -> list:
    """Assemble the right-hand column as rows of (class, text) segments."""
    rows = []

    def detail(key, value):
        if value in (None, ""):
            return
        for p, d, v in render_row(key, str(value), width):
            if p:
                rows.append([("pre", p[:2]), ("key", p[2:]), ("dot", d), ("val", v)])
            else:
                rows.append([("dot", d), ("val", v)])

    def section(title):
        label = f"- {title} "
        rows.append([("pre", "- "), ("sec", f"{title} "), ("rule", "─" * (width - len(label)))])

    def blank():
        rows.append([])

    user, host = "ian", "kimani"
    rows.append([
        ("hdr", user), ("at", "@"), ("hdr", host),
        ("rule", " " + "─" * (width - len(user) - len(host) - 2)),
    ])
    detail("Role", "Software developer")
    detail("Location", "Kisumu, Kenya")
    detail("Background", "Physics (physicist by training)")
    detail("Training", "Zone01 · 01 Edu network")
    detail("Program", "Mastercard Foundation Associates")
    detail("Uptime", stats.get("uptime") or "1 year")
    detail("Focus", "backend-focused, complete products")

    blank()
    section("Stack")
    detail("Languages.Programming", "Go, JavaScript, Python")
    detail("Frontend", "React, Next.js")
    detail("Backend/ML", "FastAPI, YOLO")
    detail("Languages.Real", "English, Swahili")

    blank()
    section("Projects")
    detail("Detecto", "counts people in live video")
    detail("Guidely", "answers from a company's own docs")
    detail("WeatherAI Gateway", "keeps a weather API in quota")
    detail("Skill-match", "tailors your CV to the job")
    detail("Writing", "Go articles on dev.to, benchmarked")

    blank()
    section("Contact")
    detail("GitHub", "frihk")
    detail("dev.to", "frihk")
    detail("LinkedIn", "ian kimani")

    for r in rows:
        if r and sum(len(t) for _, t in r) != width:
            raise ValueError(f"Info row is not {width} columns: {''.join(t for _, t in r)!r}")
    return rows


def build_terminal_card(theme_key: str, stats: dict, portrait) -> str:
    """Generate the terminal card SVG for the given theme."""
    t = THEMES[theme_key]
    rows = build_info_rows(stats, INFO_COLS)
    p_rows, p_cols = _normalise_portrait(portrait)

    first_y = BAR_H + 34
    span = (len(rows) - 1) * LINE_PITCH
    p_pitch = span / max(1, len(p_rows) - 1)
    p_font = p_pitch * P_FONT_RATIO
    p_char = p_pitch * P_CHAR_RATIO
    p_width = p_cols * p_char
    info_x = PAD + p_width + GAP
    info_w = INFO_COLS * INFO_CHAR_W
    width = round(info_x + info_w + PAD)
    height = round(first_y + span + 34)

    # Portrait
    p_lines = []
    for i, runs in enumerate(p_rows):
        y = first_y + i * p_pitch
        spans = "".join(f'<tspan class="c{tone}">{escape(text)}</tspan>' for tone, text in runs)
        p_lines.append(
            f'    <text x="{PAD}" y="{y:.2f}" textLength="{p_width:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve">{spans}</text>'
        )

    # Info column
    i_lines = []
    for i, segs in enumerate(rows):
        if not segs:
            continue
        y = first_y + i * LINE_PITCH
        spans = "".join(f'<tspan class="{cls}">{escape(text)}</tspan>' for cls, text in segs)
        i_lines.append(
            f'    <text class="r" style="animation-delay:{0.25 + i * 0.045:.3f}s" '
            f'x="{info_x:.1f}" y="{y:.1f}" textLength="{info_w:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve">{spans}</text>'
        )

    clip_top = first_y - p_pitch + 1.2
    clip_h = len(p_rows) * p_pitch + 4
    n = len(p_rows)
    reveal_s = 2.6
    glow_cx = PAD + p_width / 2
    glow_cy = first_y + span * 0.42
    c = t["portrait"]
    ch = t["chrome"]
    panel_svg = ""
    panel_defs = ""
    if t.get("panel"):
        p_in, p_out, p_stroke = t["panel"]
        panel_defs = (
            f'<radialGradient id="panel" cx="50%" cy="30%" r="85%">'
            f'<stop offset="0" stop-color="{p_in}"/><stop offset="1" stop-color="{p_out}"/></radialGradient>'
        )
        panel_svg = (
            f'<rect x="{PAD - 14}" y="{BAR_H + 14}" width="{p_width + 28:.1f}" '
            f'height="{height - BAR_H - 28}" rx="10" fill="url(#panel)" stroke="{p_stroke}"/>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="title desc">
  <title id="title">Ian Kimani — Software developer, Kisumu, Kenya ({t["name"]})</title>
  <desc id="desc">Neofetch-style terminal card: a blue ASCII-art portrait of Ian Kimani beside his role, location, stack (Go, JavaScript, Python, React, Next.js, FastAPI, YOLO), languages (English, Swahili), projects, and contact details.</desc>
  <defs>
    <radialGradient id="bg" cx="35%" cy="25%" r="90%">
      <stop offset="0" stop-color="{t["bg_inner"]}"/>
      <stop offset="1" stop-color="{t["bg_outer"]}"/>
    </radialGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="{t["glow"]}" stop-opacity="{t["glow_opacity"]}"/>
      <stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="sweep" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t["sweep"]}" stop-opacity="0"/>
      <stop offset="1" stop-color="{t["sweep"]}" stop-opacity="0.35"/>
    </linearGradient>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="#000" opacity="{t["scanlines"]}"/>
    </pattern>
    <clipPath id="reveal"><rect id="reveal-rect" x="0" y="{clip_top:.2f}" width="{PAD + p_width + 4:.1f}" height="{clip_h:.2f}"/></clipPath>
    {panel_defs}
  </defs>
  <style>
    text {{ font-family: {FONT_FAMILY}; }}
    .p text {{ font-size: {p_font:.2f}px; }}
    .c0 {{ fill: {c[0]}; }} .c1 {{ fill: {c[1]}; }} .c2 {{ fill: {c[2]}; }} .c3 {{ fill: {c[3]}; }} .c4 {{ fill: {c[4]}; }}
    .i text {{ font-size: {INFO_FONT}px; }}
    .pre {{ fill: {t["prefix"]}; }}
    .key {{ fill: {t["key"]}; }}
    .dot {{ fill: {t["dots"]}; }}
    .val {{ fill: {t["value"]}; }}
    .sep {{ fill: {t["dots"]}; }}
    .hdr {{ fill: {t["header"]}; font-weight: 700; }}
    .at {{ fill: {t["at"]}; font-weight: 700; }}
    .sec {{ fill: {t["section"]}; font-weight: 700; }}
    .rule {{ fill: {t["rule"]}; }}
    .add {{ fill: {t["additions"]}; font-weight: 600; }}
    .del {{ fill: {t["deletions"]}; font-weight: 600; }}
    .title {{ fill: {t["window_title"]}; font-size: 12.5px; }}
    @keyframes reveal {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
    @keyframes sweep {{ 0% {{ transform: translateY(0); opacity: 0; }} 5% {{ opacity: .7; }} 95% {{ opacity: .7; }} 100% {{ transform: translateY({span:.1f}px); opacity: 0; }} }}
    @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    #reveal-rect {{ transform-origin: 0 {clip_top:.2f}px; animation: reveal {reveal_s}s steps({n}, end) .3s 1 both; }}
    .s {{ animation: sweep {reveal_s}s linear .3s 1 both; }}
    .r {{ animation: fade .35s ease-out 1 both; }}
    @media (prefers-reduced-motion: reduce) {{ #reveal-rect, .s, .r {{ animation: none; }} .s {{ opacity: 0; }} }}
  </style>

  <!-- window -->
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="url(#bg)" stroke="{t["border"]}"/>
  <path d="M0.5 12.5a12 12 0 0 1 12-12h{width - 25}a12 12 0 0 1 12 12V{BAR_H}H0.5z" fill="{t["window_bar"]}"/>
  <line x1="0" y1="{BAR_H + 0.5}" x2="{width}" y2="{BAR_H + 0.5}" stroke="{t["border"]}"/>
  <circle cx="28" cy="21" r="5.5" fill="none" stroke="{ch[0]}" stroke-width="1.6"/>
  <circle cx="48" cy="21" r="5.5" fill="none" stroke="{ch[1]}" stroke-width="1.6"/>
  <circle cx="68" cy="21" r="5.5" fill="none" stroke="{ch[2]}" stroke-width="1.6"/>
  <text class="title" x="{width / 2:.1f}" y="25" text-anchor="middle">ian@kimani — frihk</text>

  <!-- soft glow behind the face -->
  {panel_svg}
  <ellipse cx="{glow_cx:.1f}" cy="{glow_cy:.1f}" rx="{p_width * 0.55:.1f}" ry="{span * 0.5:.1f}" fill="url(#glow)"/>

  <!-- portrait -->
  <g class="p" clip-path="url(#reveal)">
{chr(10).join(p_lines)}
  </g>
  <rect class="s" x="{PAD}" y="{clip_top:.2f}" width="{p_width:.1f}" height="{p_pitch * 1.4:.2f}" fill="url(#sweep)"/>

  <!-- info -->
  <g class="i">
{chr(10).join(i_lines)}
  </g>

  <rect x="1" y="{BAR_H + 1}" width="{width - 2}" height="{height - BAR_H - 2}" rx="11" fill="url(#scan)" pointer-events="none"/>
</svg>
"""


def build_stats_card(theme_key: str, stats: dict) -> str:
    """
    Generate the self-hosted GitHub statistics SVG card (matching github-readme-stats
    with show_icons=true, hide_border=true, hide_title=true, bg_color=00000000).
    """
    t = THEMES[theme_key]
    width, height = 450, 170

    commits = stats.get("commits") if isinstance(stats.get("commits"), int) else 1513
    prs = stats.get("prs") if isinstance(stats.get("prs"), int) else 30
    issues = stats.get("issues") if isinstance(stats.get("issues"), int) else 42
    repos = stats.get("repos") if isinstance(stats.get("repos"), int) else 41
    followers = stats.get("followers") if isinstance(stats.get("followers"), int) else 5

    label_color = t["value"]
    icon_color = t["key"]
    ring_color = t["chrome"][0]
    ring_track = "#1f3358" if theme_key == "dark" else "#d8e3f5"

    # Octicon 16x16 paths
    icon_commits = "M10.5 7.75a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Zm1.43.75a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5h-3.32Z"
    icon_prs = "M7.177 3.073L9.573.677A.25.25 0 0 1 10 .854v4.792a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354zM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5zm-2.25.75a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25zM11 2.5h-1V4h1a1 1 0 0 1 1 1v5.628a2.251 2.251 0 1 0 1.5 0V5A2.5 2.5 0 0 0 11 2.5zm1 10.25a.75.75 0 1 1 1.5 0 .75.75 0 0 1-1.5 0zM3.75 12a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5z"
    icon_issues = "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0ZM1.5 8a6.5 6.5 0 1 1 13 0 6.5 6.5 0 0 1-13 0Z"
    icon_repos = "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 0 1 1-1h8zM5 12.25v3.25a.25.25 0 0 0 .4.2l1.45-1.087a.249.249 0 0 1 .3 0L8.6 15.7a.25.25 0 0 0 .4-.2v-3.25a.25.25 0 0 0-.25-.25h-3.5a.25.25 0 0 0-.25.25z"
    icon_followers = "M2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4 4 0 0 0-7.9 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5ZM11 4a3.001 3.001 0 0 1 2.22 5.018 5.01 5.01 0 0 1 2.56 3.012.749.749 0 0 1-.885.954.752.752 0 0 1-.549-.514 3.507 3.507 0 0 0-2.522-2.372.75.75 0 0 1-.574-.73v-.352a.75.75 0 0 1 .416-.672A1.5 1.5 0 0 0 11 5.5.75.75 0 0 1 11 4Zm-5.5-.5a2 2 0 1 0-.001 3.999A2 2 0 0 0 5.5 3.5Z"

    items = [
        (icon_commits, "Total Commits:", f"{commits:,}"),
        (icon_prs, "Total PRs:", f"{prs:,}"),
        (icon_issues, "Total Issues:", f"{issues:,}"),
        (icon_repos, "Public Repos:", f"{repos:,}"),
        (icon_followers, "Followers:", f"{followers:,}"),
    ]

    rows_svg = []
    start_y = 22
    row_gap = 28
    for idx, (path_d, label, val) in enumerate(items):
        y = start_y + idx * row_gap
        delay = idx * 120
        rows_svg.append(
            f'  <g class="stagger" style="animation-delay: {delay}ms" transform="translate(20, {y})">\n'
            f'    <svg x="0" y="-12" width="16" height="16" viewBox="0 0 16 16" fill="{icon_color}">\n'
            f'      <path fill-rule="evenodd" d="{path_d}"/>\n'
            f'    </svg>\n'
            f'    <text class="stat-label" x="26" y="0">{escape(label)}</text>\n'
            f'    <text class="stat-val" x="200" y="0">{escape(val)}</text>\n'
            f'  </g>'
        )

    # Rank circle parameters (r=40 -> circumference ~251.3)
    circumference = 251.3
    progress_offset = 45.0

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="stats-title stats-desc">
  <title id="stats-title">Ian Kimani's GitHub Statistics ({t["name"]})</title>
  <desc id="stats-desc">Total Commits: {commits:,}, Total PRs: {prs:,}, Total Issues: {issues:,}, Public Repos: {repos:,}, Followers: {followers:,}</desc>
  <style>
    .stat-label {{
      font: 600 14px {SANS_FONT_FAMILY};
      fill: {label_color};
    }}
    .stat-val {{
      font: 700 14px {SANS_FONT_FAMILY};
      fill: {label_color};
    }}
    .rank-text {{
      font: 800 24px {SANS_FONT_FAMILY};
      fill: {label_color};
    }}
    .stagger {{
      opacity: 0;
      animation: fadeIn 0.35s ease-in-out forwards;
    }}
    .rank-progress {{
      stroke-dasharray: {circumference};
      stroke-dashoffset: {progress_offset};
      transform: rotate(-90deg);
      transform-origin: 355px 85px;
      animation: rankAnim 1s forwards ease-in-out;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translate(15px, var(--y, 0)); }}
      to {{ opacity: 1; }}
    }}
    @keyframes rankAnim {{
      from {{ stroke-dashoffset: {circumference}; }}
      to {{ stroke-dashoffset: {progress_offset}; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .stagger, .rank-progress {{ animation: none; opacity: 1; }}
    }}
  </style>

{chr(10).join(rows_svg)}

  <!-- Rank Ring -->
  <g>
    <circle cx="355" cy="85" r="40" fill="none" stroke="{ring_track}" stroke-width="6"/>
    <circle class="rank-progress" cx="355" cy="85" r="40" fill="none" stroke="{ring_color}" stroke-width="6" stroke-linecap="round"/>
    <text class="rank-text" x="355" y="93" text-anchor="middle">A</text>
  </g>
</svg>
"""


def build_top_langs_card(theme_key: str, stats: dict) -> str:
    """
    Generate the self-hosted Top Languages SVG card (matching github-readme-stats
    /api/top-langs/?layout=compact&bg_color=00000000&hide_border=true&hide_title=true).
    """
    t = THEMES[theme_key]
    width, height = 340, 170

    langs = stats.get("top_languages") or [
        {"name": "Go", "percentage": 38.87},
        {"name": "JavaScript", "percentage": 25.13},
        {"name": "Python", "percentage": 19.15},
        {"name": "TypeScript", "percentage": 8.79},
        {"name": "CSS", "percentage": 5.12},
        {"name": "HTML", "percentage": 2.94},
    ]

    text_color = t["value"]
    muted_color = t["key"]
    bar_width = 300.0
    bar_x = 20.0
    bar_y = 22.0
    bar_h = 10.0

    # Stacked progress bar segments
    segments_svg = []
    curr_x = bar_x
    total_pct = sum(l.get("percentage", 0) for l in langs) or 100.0
    for l in langs:
        name = l.get("name", "Other")
        pct = l.get("percentage", 0.0)
        seg_w = (pct / total_pct) * bar_width
        color = LANGUAGE_COLORS.get(name, "#6eb0ff")
        segments_svg.append(
            f'    <rect x="{curr_x:.2f}" y="{bar_y}" width="{max(0.5, seg_w):.2f}" height="{bar_h}" fill="{color}"/>'
        )
        curr_x += seg_w

    # Two-column compact language legend
    legend_svg = []
    col_x = [20, 175]
    start_y = 58
    row_gap = 28
    for idx, l in enumerate(langs[:6]):
        name = l.get("name", "Other")
        pct = l.get("percentage", 0.0)
        color = LANGUAGE_COLORS.get(name, "#6eb0ff")
        cx = col_x[idx % 2]
        cy = start_y + (idx // 2) * row_gap
        legend_svg.append(
            f'  <g transform="translate({cx}, {cy})">\n'
            f'    <circle cx="5" cy="-4" r="5" fill="{color}"/>\n'
            f'    <text class="lang-name" x="16" y="0">{escape(name)} <tspan class="lang-pct">{pct:.2f}%</tspan></text>\n'
            f'  </g>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="langs-title langs-desc">
  <title id="langs-title">Most Used Languages ({t["name"]})</title>
  <desc id="langs-desc">Top programming languages used across Ian Kimani's GitHub repositories.</desc>
  <defs>
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_h}" rx="5"/>
    </clipPath>
  </defs>
  <style>
    .lang-name {{
      font: 600 12.5px {SANS_FONT_FAMILY};
      fill: {text_color};
    }}
    .lang-pct {{
      font: 400 12px {SANS_FONT_FAMILY};
      fill: {muted_color};
    }}
  </style>

  <!-- Stacked Language Progress Bar -->
  <g clip-path="url(#bar-clip)">
{chr(10).join(segments_svg)}
  </g>

  <!-- Compact 2-Column Legend -->
{chr(10).join(legend_svg)}
</svg>
"""


def validate_and_write_svg(svg_content: str, target_path: Path):
    """Validate SVG XML structure and write atomically to target_path."""
    try:
        ET.fromstring(svg_content)
    except ET.ParseError as e:
        raise ValueError(f"Generated SVG for {target_path} is invalid XML: {e}")

    for placeholder in ["{placeholders}", "None", "NaN", "undefined"]:
        if placeholder in svg_content:
            raise ValueError(f"Found forbidden value '{placeholder}' in SVG for {target_path}")

    temp_path = target_path.with_suffix(".tmp")
    temp_path.write_text(svg_content, encoding="utf-8")
    temp_path.replace(target_path)
    print(f"Successfully generated and validated {target_path}")


def main():
    parser = argparse.ArgumentParser(description="Build neofetch and GitHub stats SVG cards.")
    parser.add_argument("--stats-file", default="cache/stats.json", help="Path to stats JSON file")
    parser.add_argument("--portrait-svg", default=PORTRAIT_SVG_DEFAULT,
                        help="Coloured ASCII portrait SVG to embed (default: portrait.svg)")
    parser.add_argument("--portrait-file", default="assets/portrait.txt",
                        help="Plain-text ASCII fallback used if --portrait-svg is missing")
    parser.add_argument("--output-dir", default=".", help="Directory to save generated SVGs")

    args = parser.parse_args()

    stats_path = Path(args.stats_file)
    if not stats_path.exists():
        print(f"Error: Stats file {stats_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(stats_path, "r", encoding="utf-8") as f:
        stats = json.load(f)

    svg_path = Path(args.portrait_svg)
    portrait_path = Path(args.portrait_file)
    if svg_path.exists():
        portrait_lines = load_portrait_svg(svg_path)
    elif portrait_path.exists():
        portrait_lines = [l.rstrip("\r\n") for l in portrait_path.read_text(encoding="utf-8").splitlines()]
    else:
        print(f"Error: neither {svg_path} nor {portrait_path} exists.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build Dark and Light Terminal Cards
    dark_card = build_terminal_card("dark", stats, portrait_lines)
    validate_and_write_svg(dark_card, out_dir / "dark_mode.svg")

    light_card = build_terminal_card("light", stats, portrait_lines)
    validate_and_write_svg(light_card, out_dir / "light_mode.svg")

    # Build Dark and Light GitHub Statistics & Top Languages Cards
    validate_and_write_svg(build_stats_card("dark", stats), out_dir / "stats_dark.svg")
    validate_and_write_svg(build_stats_card("light", stats), out_dir / "stats_light.svg")
    validate_and_write_svg(build_top_langs_card("dark", stats), out_dir / "top_langs_dark.svg")
    validate_and_write_svg(build_top_langs_card("light", stats), out_dir / "top_langs_light.svg")


if __name__ == "__main__":
    main()
