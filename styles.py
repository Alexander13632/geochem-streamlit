"""styles.py

Generate colour, symbol and size maps for Streamlit geo‑plot app.
Known `type` values take fixed styles (see TYPE_STYLES).
All unknown types receive deterministic random colours & symbols so that
nothing is left unstyled.
"""
from __future__ import annotations
import colorsys
import random
from typing import Dict, Tuple
import pandas as pd

# ----------------------------------------------------------------------
# Pre‑defined styles for well‑known tectono‑magmatic types
# ----------------------------------------------------------------------
TYPE_STYLES: Dict[str, Dict[str, str | int]] = {
    "MORB":   {"symbol": "circle",      "base_color": "#444444", "size": 15},
    "OIB":    {"symbol": "square",      "base_color": "#0060ff", "size": 20},
    "sediments":    {"symbol": "triangle-down",      "base_color": "#ffd000", "size": 20},
    "arc":    {"symbol": "triangle-up", "base_color": "#00c83e", "size": 20},
    "Deccan": {"symbol": "cross",       "base_color": "#ff0000", "size": 30},
}

# Pool of symbols to choose for unknown types (avoid duplicates)
AVAILABLE_SYMBOLS = [
    "circle", "square", "diamond", "triangle-up", "triangle-down",
    "cross", "x", "star", "hexagon", "pentagon",
    "triangle-left", "triangle-right", "hexagon2",
    "star-diamond", "asterisk",
]

# ----------------------------------------------------------------------
# Helper
# ----------------------------------------------------------------------

def _rgb_hex(r: float, g: float, b: float) -> str:
    """Convert 0‑1 floats to #RRGGBB."""
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------

def build_style_maps(
    df: pd.DataFrame,
    *,
    type_col: str = "type",
    loc_col: str = "Location",
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, int]]:
    """Return (color_map, symbol_map, size_map).

    * **color_map**  maps every Location value → hex colour.
    * **symbol_map** maps every Type value     → marker symbol.
    * **size_map**   maps every Type value     → marker size in px.
    Unknown `type` values are assigned random symbol/colour, deterministic with seed 42.
    """
    rng = random.Random(42)

    color_map: Dict[str, str] = {}
    symbol_map: Dict[str, str] = {}
    size_map: Dict[str, int] = {}

    used_symbols = set(val["symbol"] for val in TYPE_STYLES.values())

    # iterate over each type
    for t_val, sub_df in df.groupby(type_col):
        t_key = str(t_val)

        if t_key in TYPE_STYLES:  # known style
            style = TYPE_STYLES[t_key]
        else:  # generate new random style
            # unique random symbol
            sym_choices = [s for s in AVAILABLE_SYMBOLS if s not in used_symbols]
            if not sym_choices:
                sym_choices = AVAILABLE_SYMBOLS  # fallback allow repeats
            symbol = rng.choice(sym_choices)
            used_symbols.add(symbol)
            # random colour
            base_color = _rgb_hex(rng.random(), rng.random(), rng.random())
            style = {"symbol": symbol, "base_color": base_color, "size": 18}

        symbol_map[t_key] = style["symbol"]
        size_map[t_key]   = int(style["size"])

        # convert base colour to HSV for lightness variation
        base_hex = style["base_color"].lstrip("#")
        br, bg, bb = (int(base_hex[i:i+2], 16)/255 for i in (0, 2, 4))
        h, s, _ = colorsys.rgb_to_hsv(br, bg, bb)

        loc_values = sorted(sub_df[loc_col].dropna().unique())
        n = max(1, len(loc_values) - 1)
        for i, loc in enumerate(loc_values):
            v = 0.6 + 0.4 * (i / n)  # brightness 60‑100 %
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            type_loc_key = f"{t_key}|{loc}"           # t_key = текущий type
            color_map[type_loc_key] = _rgb_hex(r, g, b)


    # ensure every location has a colour (edge case if groupby filtered)
    for loc in df[loc_col].dropna().unique():
        color_map.setdefault(str(loc), _rgb_hex(rng.random(), rng.random(), rng.random()))

    return color_map, symbol_map, size_map