
from styles import AVAILABLE_SYMBOLS  # если нужно
import streamlit as st
import random
import pandas as pd

def default_style_editor(df, color_map_user=None, symbol_map_user=None, size_map_user=None, styles=None):
    if color_map_user is None:
        color_map_user = {}
    if symbol_map_user is None:
        symbol_map_user = {}
    if size_map_user is None:
        size_map_user = {}
    if styles is None:
        styles = {}

    pre_symbols = AVAILABLE_SYMBOLS.copy()
    random.seed(42)

    for key in sorted(df["type_loc"].dropna().unique()):
        # key = 'Amphibolite|Himalaya', например
        # Всё только по key!
        cur_color  = color_map_user.get(key, "#1f77b4")
        cur_symbol = symbol_map_user.get(key, "circle")
        cur_size   = size_map_user.get(key, 20)
        with st.sidebar.expander(key, expanded=False):
            color  = st.color_picker("Color", cur_color, key=f"col_{key}")
            sym_idx = pre_symbols.index(cur_symbol) if cur_symbol in pre_symbols else 0
            symbol = st.selectbox("Symbol", pre_symbols, index=sym_idx, key=f"sym_{key}")
            size   = st.slider("Size (px)", 2, 80, cur_size, key=f"sz_{key}")
            alpha  = st.slider("Opacity (%)", 10, 100, 90, key=f"op_{key}") / 100
            outcol = st.color_picker("Outline", "#000000", key=f"out_{key}")
            outwid = st.slider("Outline width", 1.0, 6.0, 1.0, 0.5, key=f"ow_{key}")

            # — обновляем ТОЛЬКО по key!
            color_map_user[key] = color
            symbol_map_user[key] = symbol
            size_map_user[key] = size
            styles[key] = {
                "opacity": alpha,
                "outline_color": outcol,
                "outline_width": outwid,
            }
    return color_map_user, symbol_map_user, size_map_user, styles



def inherit_styles_from_typeloc(
    df: pd.DataFrame,
    group_col: str,
    base_color: dict,      # ключи «type|Location»
    base_symbol: dict,     # ключи «type»
    base_size: dict        # ключи «type»
):
    """Собирает color / symbol / size-карты для переменной group_col
    (например, «To plot») на основе уже существующих карт."""
    color_map, symbol_map, size_map = {}, {}, {}
    unique_groups = df[group_col].dropna().unique()

    for g in unique_groups:
        # Берём первый непустой образец внутри этой группы
        row = df.loc[df[group_col] == g].iloc[0]

        typ          = str(row["type"])
        type_loc_key = f"{row['type']}|{row['Location']}"

        color_map[g]  = base_color.get(type_loc_key, "#1f77b4")
        symbol_map[g] = base_symbol.get(typ, "circle")
        size_map[g]   = base_size.get(typ, 20)

    return color_map, symbol_map, size_map

