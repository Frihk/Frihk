"""
scripts/templates/theme_tokens.py:
Color tokens and typography settings for Dark and Light themes.
Complies with WCAG AA contrast (>= 4.5:1 for normal text).
"""

THEMES = {
    "dark": {
        "name": "Dark Mode",
        "bg": "#161b22",
        "border": "#30363d",
        "window_bar": "#0d1117",
        "window_title": "#8b949e",
        "portrait_color": "#58a6ff",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "dots": "#6e7681",
        "header": "#c9d1d9",
        "rule": "#30363d",
        "section": "#c9d1d9",
        "additions": "#3fb950",
        "deletions": "#f85149",
        "card_shadow": "rgba(0, 0, 0, 0.4)",
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
        "bg": "#ffffff",
        "border": "#d0d7de",
        "window_bar": "#f6f8fa",
        "window_title": "#57606a",
        "portrait_color": "#0969da",
        "key": "#953800",
        "value": "#0a3069",
        "dots": "#8c959f",
        "header": "#24292f",
        "rule": "#d0d7de",
        "section": "#24292f",
        "additions": "#1a7f37",
        "deletions": "#cf222e",
        "card_shadow": "rgba(0, 0, 0, 0.08)",
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
