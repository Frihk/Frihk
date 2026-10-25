#!/usr/bin/env python3
"""
Generate an animated terminal SVG for GitHub Profile README.
Pure CSS keyframe animation, valid standalone SVG, 0 external dependencies.
"""

import html
import re

# ==============================================================================
# CONFIGURATION & THEME
# ==============================================================================

PALETTE = {
    "bg": "#0c0e11",
    "topbar_bg": "#14171d",
    "border": "#232731",
    "amber": "#ffb000",
    "teal": "#5fd7c4",
    "text": "#e8e1d0",
    "dim": "#7d7358",
    "cursor": "#ffb000",
}

FONT_STACK = "ui-monospace, 'SF Mono', Menlo, 'DejaVu Sans Mono', 'Courier New', monospace"
FONT_SIZE = 14
LINE_HEIGHT = 22
CHAR_WIDTH_EM = 0.6  # em per char approx for monospace
EM_PX = FONT_SIZE * CHAR_WIDTH_EM  # ~8.4px per char

SVG_WIDTH = 820
PAD_X = 28
TOPBAR_HEIGHT = 40
PAD_Y = 24
BOTTOM_PAD = 36

HOLD_TIME = 7.0  # seconds to hold finished state before loop restart
CMD_SPEED = 0.048  # seconds per char for commands
OUTPUT_SPEED = 0.012  # seconds per char for output
PAUSE_AFTER_LINE = 0.28  # pause between steps
PAUSE_AFTER_CMD = 0.45  # extra pause before output begins

# ==============================================================================
# CONTENT SPECIFICATION
# Type: 'cmd' (slow typing with prompt) | 'out' (fast print) | 'blank'
# Tokens inside text:
# [amber]...[/amber], [teal]...[/teal], [dim]...[/dim], [text]...[/text]
# ==============================================================================

SCRIPT = [
    {
        "type": "cmd",
        "text": "cat ~/portrait.txt | sed -n '21,34p'",
    },
    {"type": "out", "text": "[dim]^%%^:%@%^^%^_````_``^^^%@@@@@@@@@@Z@@%^_______,,,,Z%<Z@Z@@[/dim]"},
    {"type": "out", "text": "[dim]|Z%^Z@*^^^``````````~._````____________         ^^^-~<>,^%[/dim]"},
    {"type": "out", "text": "[dim]J%@/`-^^^``________      ```^^^^^^^`^`      ________`_^^^%[/dim]"},
    {"type": "out", "text": "[dim]__2 -`     `__,,Z_``       ___,;;__'       ```_,,___````-^[/dim]"},
    {"type": "out", "text": "[dim]?%\\.`      `````` `        ^^^ZZZ^^`              _`^~___:[/dim]"},
    {"type": "out", "text": "[dim]~~~,:__     _@C  `  z__ -_  ::@@@@@C_  .   _@_   `_S@_____:[/dim]"},
    {"type": "out", "text": "[dim]_^C`______ .^%;___;7^^,,   _^@@@@@%_ _ ..__^%___z@F^-^:;:%[/dim]"},
    {"type": "out", "text": "[dim]`^@ :_:%;:_ `^^^~^^^``__`__:@@@@@@@%>`::___`^^^^``__<%%%@%[/dim]"},
    {"type": "out", "text": "[dim]_ @L-_Z@@%;__    ___:%%^_`_@@@@@@@@@^%_%%^^:__  ___:%@@@@@[/dim]"},
    {"type": "out", "text": "[dim]@;Z/:^ZZ@@%%%::_..-_:/_/^_@@@@@@@@@@@/Z%_%@:^:::_:%@@@@@F,[/dim]"},
    {"type": "out", "text": "[dim]ZCJL`%,^Z@@%%^;:__>^,@%^_@@@@@@@@@@@@@%ZZ@,^%%;;%%Z@ZF^u@@[/dim]"},
    {"type": "out", "text": "[dim]^@@C::^^%>ZZZZZZu@@@@Z%_@@@@@@@@@@@@@@@@%@@@@@@@@<@@%ZZ@@@[/dim]"},
    {"type": "out", "text": "[dim] ^^S_`^%%%%@@@@@@@@@S%_@@@@@@@@@@@@@@@@@@^%@@@@@@@@@ZZ%%Z%[/dim]"},
    {"type": "out", "text": "[dim] ;:?C_`:^%%%@@@@@@@@@@@@@@Z%@@@@@@ZZZ@@@@@%@@%ZZ@@@@@%@Z%%[/dim]"},
    {
        "type": "blank",
        "text": "",
    },
    {
        "type": "cmd",
        "text": "cat about.txt",
    },
    {
        "type": "out",
        "text": "[dim]background :[/dim] Physics graduate, transitioning into backend engineering",
    },
    {
        "type": "out",
        "text": "[dim]training   :[/dim] Zone01 bootcamp",
    },
    {
        "type": "out",
        "text": "[dim]work       :[/dim] AI data labeling reviewer [dim](egocentric video annotation)[/dim]",
    },
    {
        "type": "blank",
        "text": "",
    },
    {
        "type": "cmd",
        "text": "ls -l stack/",
    },
    {
        "type": "out",
        "text": "[dim]core_backend [/dim] [teal]go[/teal]   [teal]python[/teal]",
    },
    {
        "type": "out",
        "text": "[dim]web_systems  [/dim] [text]javascript[/text]   [text]react[/text]   [text]next.js[/text]",
    },
    {
        "type": "blank",
        "text": "",
    },
    {
        "type": "cmd",
        "text": "curl -s https://api.frihk.dev/pipeline | progress",
    },
    {
        "type": "out",
        "text": "[amber][########################################][/amber] [teal]100%[/teal]",
    },
    {
        "type": "out",
        "text": "[dim]sync:[/dim] [text]zone01_curriculum -> video_annotation_ops -> backend_services[/text]",
    },
    {
        "type": "blank",
        "text": "",
    },
    {
        "type": "cmd",
        "text": "gh stats --telemetry --user=Frihk",
    },
    {
        "type": "out",
        "text": "[dim]┌─ PERFORMANCE & TELEMETRY ─────────────────────────────────────┐[/dim]",
    },
    {
        "type": "out",
        "text": "[dim]│[/dim] [text]Repos:[/text] [amber]39[/amber]  [dim]│[/dim] [text]Followers:[/text] [teal]5[/teal]  [dim]│[/dim] [text]Status:[/text] [teal]ACTIVE[/teal]  [dim]│[/dim] [text]Uptime:[/text] [amber]99.98%[/amber]   [dim]│[/dim]",
    },
    {
        "type": "out",
        "text": "[dim]│[/dim] [text]Go        [/text] [amber]████████████████████[/amber] [dim]44%[/dim]                                  [dim]│[/dim]",
    },
    {
        "type": "out",
        "text": "[dim]│[/dim] [text]JS/Next   [/text] [teal]████████████████[/teal]     [dim]36%[/dim]                                  [dim]│[/dim]",
    },
    {
        "type": "out",
        "text": "[dim]│[/dim] [text]Python    [/text] [dim]████████[/dim]             [dim]16%[/dim]                                  [dim]│[/dim]",
    },
    {
        "type": "out",
        "text": "[dim]└───────────────────────────────────────────────────────────────┘[/dim]",
    },
    {
        "type": "blank",
        "text": "",
    },
    {
        "type": "cmd",
        "text": "git status --hiring",
    },
    {
        "type": "out",
        "text": "[dim]status:[/dim] [amber]OPEN[/amber] [dim]—[/dim] [text]available for junior roles & open-source collaborations[/text]",
    },
]


def strip_tags(text: str) -> str:
    """Strip styling tags to get raw display string."""
    return re.sub(r"\[(amber|teal|dim|text)\]|\[\/(amber|teal|dim|text)\]", "", text)


def parse_spans_to_svg(text: str, default_color: str) -> str:
    """Convert custom tags to SVG <tspan> elements."""
    pattern = r"(\[(amber|teal|dim|text)\](.*?)\[\/\2\])"
    parts = []
    last_idx = 0

    for match in re.finditer(pattern, text):
        start, end = match.span()
        if start > last_idx:
            raw = text[last_idx:start]
            if raw:
                parts.append(
                    f'<tspan fill="{default_color}">{html.escape(raw)}</tspan>'
                )
        tag_color_name = match.group(2)
        color_val = PALETTE.get(tag_color_name, default_color)
        content = match.group(3)
        parts.append(f'<tspan fill="{color_val}">{html.escape(content)}</tspan>')
        last_idx = end

    if last_idx < len(text):
        raw = text[last_idx:]
        if raw:
            parts.append(f'<tspan fill="{default_color}">{html.escape(raw)}</tspan>')

    if not parts:
        return html.escape(text)
    return "".join(parts)


def generate_svg() -> str:
    # 1. Timeline computation
    lines_meta = []
    current_time = 0.5  # initial slight breath before first command typing

    for idx, item in enumerate(SCRIPT):
        item_type = item["type"]
        raw_text = strip_tags(item["text"])

        if item_type == "cmd":
            prompt = "ian@kisumu:~$ "
            full_raw = prompt + raw_text
            char_count = max(len(raw_text), 1)
            duration = max(char_count * CMD_SPEED, 0.2)
            start_time = current_time
            end_time = start_time + duration
            current_time = end_time + PAUSE_AFTER_CMD
            lines_meta.append(
                {
                    "idx": idx,
                    "type": "cmd",
                    "prompt": prompt,
                    "text": item["text"],
                    "raw_text": raw_text,
                    "full_raw": full_raw,
                    "char_count": char_count,
                    "start": start_time,
                    "end": end_time,
                    "duration": duration,
                }
            )
        elif item_type == "out":
            char_count = max(len(raw_text), 1)
            duration = max(char_count * OUTPUT_SPEED, 0.12)
            start_time = current_time
            end_time = start_time + duration
            current_time = end_time + PAUSE_AFTER_LINE
            lines_meta.append(
                {
                    "idx": idx,
                    "type": "out",
                    "prompt": "",
                    "text": item["text"],
                    "raw_text": raw_text,
                    "full_raw": raw_text,
                    "char_count": char_count,
                    "start": start_time,
                    "end": end_time,
                    "duration": duration,
                }
            )
        else:  # blank
            lines_meta.append(
                {
                    "idx": idx,
                    "type": "blank",
                    "prompt": "",
                    "text": "",
                    "raw_text": "",
                    "full_raw": "",
                    "char_count": 0,
                    "start": current_time,
                    "end": current_time,
                    "duration": 0,
                }
            )
            current_time += 0.1

    final_typing_end = current_time
    total_cycle = final_typing_end + HOLD_TIME
    fade_restart_start = final_typing_end + HOLD_TIME - 0.4

    # SVG Height computation
    content_lines_count = len(lines_meta) + 1  # +1 for active cursor line
    svg_height = (
        TOPBAR_HEIGHT + PAD_Y + (content_lines_count * LINE_HEIGHT) + BOTTOM_PAD
    )

    # 2. Keyframes and CSS generation
    css_rules = []

    # Container fade-out and reset at cycle end
    k_fade_pct_start = (fade_restart_start / total_cycle) * 100
    css_rules.append(f"""
    @keyframes termCycle {{
      0% {{ opacity: 1; }}
      {k_fade_pct_start:.2f}% {{ opacity: 1; }}
      99.3% {{ opacity: 0; }}
      100% {{ opacity: 0; }}
    }}
    .terminal-content {{
      animation: termCycle {total_cycle:.2f}s infinite;
    }}
    """)

    # Cursor blink
    css_rules.append("""
    @keyframes blink {
      0%, 49% { opacity: 1; }
      50%, 100% { opacity: 0; }
    }
    .blinking-cursor {
      animation: blink 0.9s infinite;
    }
    """)

    # Individual line animations
    for line in lines_meta:
        if line["type"] == "blank":
            continue

        l_idx = line["idx"]
        t_start = line["start"]
        t_end = line["end"]

        p_start = (t_start / total_cycle) * 100
        p_end = (t_end / total_cycle) * 100
        steps = line["char_count"]

        # Reveal clip rect via scaleX
        clip_kf = f"reveal-line-{l_idx}"
        css_rules.append(f"""
        @keyframes {clip_kf} {{
          0%, {p_start:.2f}% {{
            transform: scaleX(0);
          }}
          {p_end:.2f}%, 100% {{
            transform: scaleX(1);
          }}
        }}
        #clip-rect-{l_idx} {{
          animation: {clip_kf} {total_cycle:.2f}s steps({steps}, end) infinite;
        }}
        """)

    css_block = "\n".join(css_rules)

    # 3. SVG Nodes construction
    clip_defs = []
    text_nodes = []

    running_y = TOPBAR_HEIGHT + PAD_Y + LINE_HEIGHT

    for line in lines_meta:
        l_idx = line["idx"]
        l_type = line["type"]

        if l_type == "blank":
            running_y += LINE_HEIGHT
            continue

        prompt_str = line["prompt"]
        text_str = line["text"]
        raw_line_len = len(line["full_raw"])
        clip_width = max(int(raw_line_len * EM_PX) + 40, 60)

        # In cmd mode, prompt is visible once typing starts
        # We wrap entire line in a clipPath that animates scaleX(0 -> 1)
        clip_defs.append(f"""
      <clipPath id="clip-{l_idx}">
        <rect id="clip-rect-{l_idx}" x="{PAD_X}" y="{running_y - LINE_HEIGHT + 4}" width="{clip_width}" height="{LINE_HEIGHT + 2}" style="transform-origin: {PAD_X}px {running_y}px;" />
      </clipPath>
        """.strip())

        if l_type == "cmd":
            prompt_svg = (
                f'<tspan fill="{PALETTE["amber"]}">{html.escape(prompt_str)}</tspan>'
            )
            body_svg = parse_spans_to_svg(text_str, PALETTE["text"])
            line_inner = prompt_svg + body_svg
        else:
            line_inner = parse_spans_to_svg(text_str, PALETTE["dim"])

        text_nodes.append(f"""
      <g clip-path="url(#clip-{l_idx})">
        <text x="{PAD_X}" y="{running_y}" font-family="{FONT_STACK}" font-size="{FONT_SIZE}" font-weight="500">{line_inner}</text>
      </g>
        """.strip())

        running_y += LINE_HEIGHT

    # Trailing active prompt + blinking cursor
    final_prompt = "ian@kisumu:~$ "
    cursor_x = PAD_X + int(len(final_prompt) * EM_PX)

    # Cursor appears when typing finishes and remains until loop resets
    cursor_appear_pct = (final_typing_end / total_cycle) * 100
    cursor_visibility_kf = f"""
    @keyframes cursorReveal {{
      0%, {cursor_appear_pct:.2f}% {{ opacity: 0; }}
      {cursor_appear_pct + 0.01:.2f}%, 100% {{ opacity: 1; }}
    }}
    .end-cursor-group {{
      animation: cursorReveal {total_cycle:.2f}s infinite;
    }}
    """
    css_block += f"\n{cursor_visibility_kf}"

    text_nodes.append(f"""
      <g class="end-cursor-group">
        <text x="{PAD_X}" y="{running_y}" font-family="{FONT_STACK}" font-size="{FONT_SIZE}" fill="{PALETTE['amber']}" font-weight="500">{html.escape(final_prompt)}</text>
        <rect class="blinking-cursor" x="{cursor_x}" y="{running_y - FONT_SIZE + 2}" width="8.5" height="{FONT_SIZE + 1}" fill="{PALETTE['cursor']}" />
      </g>
    """.strip())

    clips_combined = "\n".join(clip_defs)
    lines_combined = "\n".join(text_nodes)

    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {svg_height}" width="{SVG_WIDTH}" height="{svg_height}" role="img" aria-label="Terminal session for Ian Kimani (@frihk), Kisumu Kenya">
  <title>ian@kisumu: ~ [0.09°S, 34.76°E]</title>
  <defs>
    <linearGradient id="scanlineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.03" />
      <stop offset="50%" stop-color="#000000" stop-opacity="0.2" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.03" />
    </linearGradient>
    <pattern id="scanlines" width="100%" height="4" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="{SVG_WIDTH}" y2="0" stroke="#000000" stroke-opacity="0.22" stroke-width="1.2" />
    </pattern>
    <radialGradient id="topGlow" cx="50%" cy="0%" r="80%">
      <stop offset="0%" stop-color="{PALETTE['amber']}" stop-opacity="0.08" />
      <stop offset="100%" stop-color="{PALETTE['bg']}" stop-opacity="0" />
    </radialGradient>
    {clips_combined}
  </defs>

  <style>
    {css_block}
  </style>

  <!-- Terminal Window Background -->
  <rect x="0.5" y="0.5" width="{SVG_WIDTH - 1}" height="{svg_height - 1}" rx="8" fill="{PALETTE['bg']}" stroke="{PALETTE['border']}" stroke-width="1" />

  <!-- Top Ambient Phosphor Glow -->
  <rect x="1" y="1" width="{SVG_WIDTH - 2}" height="140" rx="8" fill="url(#topGlow)" pointer-events="none" />

  <!-- Window Header / Title Bar -->
  <path d="M 0.5 8.5 A 8 8 0 0 1 8.5 0.5 L {SVG_WIDTH - 8.5} 0.5 A 8 8 0 0 1 {SVG_WIDTH - 0.5} 8.5 L {SVG_WIDTH - 0.5} {TOPBAR_HEIGHT} L 0.5 {TOPBAR_HEIGHT} Z" fill="{PALETTE['topbar_bg']}" />
  <line x1="0.5" y1="{TOPBAR_HEIGHT}" x2="{SVG_WIDTH - 0.5}" y2="{TOPBAR_HEIGHT}" stroke="{PALETTE['border']}" stroke-width="1" />

  <!-- Hollow Ring Window Controls (Amber, Teal, Dim) -->
  <circle cx="24" cy="20" r="5" fill="none" stroke="{PALETTE['amber']}" stroke-width="1.6" />
  <circle cx="42" cy="20" r="5" fill="none" stroke="{PALETTE['teal']}" stroke-width="1.6" />
  <circle cx="60" cy="20" r="5" fill="none" stroke="{PALETTE['dim']}" stroke-width="1.6" />

  <!-- Window Title -->
  <text x="{SVG_WIDTH // 2}" y="25" text-anchor="middle" font-family="{FONT_STACK}" font-size="12" fill="{PALETTE['dim']}" letter-spacing="0.5">ian@kisumu: ~ — 0.09°S 34.76°E</text>

  <!-- Animated Terminal Body -->
  <g class="terminal-content">
    {lines_combined}
  </g>

  <!-- Scanline Overlay for Phosphor Aesthetic -->
  <rect x="1" y="{TOPBAR_HEIGHT + 1}" width="{SVG_WIDTH - 2}" height="{svg_height - TOPBAR_HEIGHT - 2}" fill="url(#scanlines)" pointer-events="none" />
</svg>
"""
    return svg_template


def main():
    svg_code = generate_svg()
    with open("terminal.svg", "w", encoding="utf-8") as f:
        f.write(svg_code)
    print(f"Generated terminal.svg successfully ({len(svg_code)} bytes).")


if __name__ == "__main__":
    main()
