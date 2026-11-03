"""
scripts/templates/theme_tokens.py:
Color tokens for the Dark and Light card themes.

The card palette is derived from the 5-tone blue ramp used by portrait.svg
(c0..c4), so the info column reads as part of the same image as the portrait.
Text tokens (key, value, header, section, additions, deletions) meet WCAG AA
(>= 4.5:1) against the card background. Dots, rules, and the leading ". " are
decorative and intentionally lower-contrast.
"""

THEMES = {
    "dark": {
        "name": "Dark Mode",
        # Window
        "bg_inner": "#0c1730",
        "bg_outer": "#060a12",
        "border": "#1c2740",
        "window_bar": "#0d1320",
        "window_title": "#6b7fa8",
        "chrome": ("#3b82f6", "#7cb7ff", "#4b5d85"),
        "glow": "#3b82f6",
        "glow_opacity": "0.16",
        "scanlines": "0.22",
        "sweep": "#7cb7ff",
        # Portrait ramp (sparse -> dense), identical to portrait.svg
        "portrait": ("#2f64e8", "#4a8cff", "#6eb0ff", "#93c8ff", "#c2e0ff"),
        # Optional framed panel behind the portrait (None = draw on the card itself)
        "panel": None,
        # Info column
        "prefix": "#3f6fd8",
        "key": "#6eb0ff",
        "value": "#dcecff",
        "dots": "#2c4470",
        "header": "#c2e0ff",
        "at": "#4a8cff",
        "rule": "#1f3358",
        "section": "#93c8ff",
        "additions": "#5eead4",
        "deletions": "#ff8fa3",
        # Contribution calendar
        "cal_bg": "#161b22",
        "cal_border": "#30363d",
        "cal_text": "#c9d1d9",
        "cal_muted": "#8b949e",
        "cal_level0": "#21262d",
        "cal_level1": "#0e4429",
        "cal_level2": "#006d32",
        "cal_level3": "#26a641",
        "cal_level4": "#39d353",
    },
    "light": {
        "name": "Light Mode",
        "bg_inner": "#f8fbff",
        "bg_outer": "#e8f0fb",
        "border": "#c8d6ee",
        "window_bar": "#e3ecfa",
        "window_title": "#4b5d85",
        "chrome": ("#2f64e8", "#6eb0ff", "#9aa9c7"),
        "glow": "#3b82f6",
        "glow_opacity": "0.16",
        "scanlines": "0",
        "sweep": "#2f64e8",
        # The ASCII art encodes brightness for a dark background, so on a light
        # page it sits on a navy panel with the original ramp (avoids a negative).
        "portrait": ("#2f64e8", "#4a8cff", "#6eb0ff", "#93c8ff", "#c2e0ff"),
        "panel": ("#0c1730", "#060a12", "#1c2740"),
        # Info column
        "prefix": "#7097dc",
        "key": "#1f56c4",
        "value": "#0b2a5c",
        "dots": "#a9bcdc",
        "header": "#0b2a5c",
        "at": "#3f6cc6",
        "rule": "#c9d7ef",
        "section": "#1f4c9e",
        "additions": "#0f7b6c",
        "deletions": "#c0365a",
        # Contribution calendar
        "cal_bg": "#ffffff",
        "cal_border": "#d0d7de",
        "cal_text": "#24292f",
        "cal_muted": "#57606a",
        "cal_level0": "#ebedf0",
        "cal_level1": "#9be9a8",
        "cal_level2": "#40c463",
        "cal_level3": "#30a14e",
        "cal_level4": "#216e39",
    },
}
