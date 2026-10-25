#!/usr/bin/env python3
"""
Make portrait.svg draw itself line by line, top to bottom, ONCE per page
load/reload, then stay fully drawn.

Re-run after you regenerate the portrait art:  python3 animate_portrait.py
Safe to run repeatedly (it strips any previous animation first).

Technique: every text line stays static; one clipPath rect grows downward with
transform: scaleY and steps(n, end), so exactly one new line appears per step.
CSS only, no script, GitHub-safe.
"""
import re

SRC = "portrait.svg"

LINE_STEP = 0.07   # seconds per line
START_DELAY = 0.4  # blank pause before the first line appears

with open(SRC, encoding="utf-8") as f:
    svg = f.read()

# --- 1. undo any previous run -------------------------------------------------
svg = re.sub(r'<clipPath id="reveal">.*?</clipPath>\s*', "", svg, flags=re.S)
svg = re.sub(r'<g id="art"[^>]*>(.*?)</g>', r"\1", svg, flags=re.S)
svg = re.sub(r"/\*PORTRAIT-ANIM\*/.*?/\*END\*/", "", svg, flags=re.S)
svg = re.sub(r'<rect class="s"[^>]*/>\s*', "", svg)
svg = re.sub(r' class="r" style="animation-delay:[\d.]+s"', "", svg)

# --- 2. locate the art lines (the <text> elements with y positions) ----------
lines = list(re.finditer(r'<text x="22" y="([\d.]+)"[^>]*>.*?</text>', svg, flags=re.S))
if len(lines) < 2:
    raise SystemExit("no art lines found in portrait.svg")
n = len(lines)
ys = [float(m.group(1)) for m in lines]
pitch = (ys[-1] - ys[0]) / (n - 1)
top = ys[0] - pitch + 1.2          # clip top edge: hides line k+1 until its step
height = n * pitch
width = float(re.search(r'<svg[^>]*\swidth="([\d.]+)"', svg).group(1))

# --- 3. timing ----------------------------------------------------------------
draw = n * LINE_STEP
cycle = START_DELAY + draw + 0.4   # runs once; the tail lets the sweep bar fade
pct = lambda t: f"{t / cycle * 100:.3f}%"
t_draw0, t_draw1 = START_DELAY, START_DELAY + draw
end_y = height - pitch

# animation-fill-mode: both + iteration-count 1 => plays once per load, then the
# last keyframe (fully drawn, bar hidden) stays in place.
css = f"""/*PORTRAIT-ANIM*/
@keyframes reveal{{0%,{pct(t_draw0)}{{transform:scaleY(0)}}{pct(t_draw1)},100%{{transform:scaleY(1)}}}}
@keyframes sweep{{0%,{pct(t_draw0)}{{transform:translateY(0);opacity:0}}{pct(t_draw0 + 0.05)}{{opacity:.7}}{pct(t_draw1)}{{transform:translateY({end_y:.2f}px);opacity:.7}}100%{{transform:translateY({end_y:.2f}px);opacity:0}}}}
#reveal-rect{{transform-origin:0 {top:.2f}px;animation:reveal {cycle:.2f}s steps({n},end) 1 both}}
.s{{animation:sweep {cycle:.2f}s linear 1 both}}
/*END*/"""

# --- 4. rebuild -----------------------------------------------------------------
svg = svg.replace("</style>", css + "</style>", 1)

defs = (f'<clipPath id="reveal"><rect id="reveal-rect" x="0" y="{top:.2f}" '
        f'width="{width:.0f}" height="{height:.2f}"/></clipPath>')
svg = svg.replace("</defs>", defs + "</defs>", 1)

first, last = lines[0].start(), lines[-1].end()
# positions shifted after the inserts above, so re-find the block
lines = list(re.finditer(r'<text x="22" y="([\d.]+)"[^>]*>.*?</text>', svg, flags=re.S))
first, last = lines[0].start(), lines[-1].end()
bar = (f'<rect class="s" x="1" y="{top:.2f}" width="{width - 2:.0f}" height="{pitch:.2f}" '
       f'fill="url(#b)"/>')
svg = (svg[:first] + '<g id="art" clip-path="url(#reveal)">' + svg[first:last]
       + "</g>" + bar + svg[last:])

with open(SRC, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"{n} lines, plays once ({draw:.1f}s drawing)")
