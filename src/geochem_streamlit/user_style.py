import random
import streamlit as st


def get_available_symbols() -> list[str]:
    """Get list of available symbols."""
    return [
        "circle",
        "square",
        "diamond",
        "cross",
        "x",
        "triangle-up",
        "triangle-down",
        "triangle-left",
        "triangle-right",
        "star",
        "hexagram",
        "star-diamond",
        "hourglass",
    ]


def generate_group_styles(groups: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    random.seed(42)  # чтобы цвета были всегда одинаковы для одной и той же группы
    colors = []
    for _ in groups:
        color = "#" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])
        colors.append(color)
    symbols = random.sample(
        get_available_symbols(), min(len(groups), len(get_available_symbols()))
    )
    # Если групп больше, чем символов, повторяем символы
    while len(symbols) < len(groups):
        symbols += random.sample(
            get_available_symbols(),
            min(len(groups) - len(symbols), len(get_available_symbols())),
        )
    color_map = dict(zip(groups, colors))
    symbol_map = dict(zip(groups, symbols))
    return color_map, symbol_map


def group_style_editor(groups, color_map, symbol_map, size_map=None, opacity_map=None):
    available_symbols = get_available_symbols()
    if size_map is None:
        size_map = {g: 20 for g in groups}
    if opacity_map is None:
        opacity_map = {g: 0.9 for g in groups}
    for group in groups:
        with st.sidebar.expander(str(group), expanded=False):
            cur_color = color_map[group]
            cur_symbol = symbol_map[group]
            cur_size = size_map.get(group, 20)
            cur_opacity = opacity_map.get(group, 0.9)
            color = st.color_picker("Color", cur_color, key=f"user_color_{group}")
            sym_idx = (
                available_symbols.index(cur_symbol)
                if cur_symbol in available_symbols
                else 0
            )
            symbol = st.selectbox(
                "Symbol",
                available_symbols,
                index=sym_idx,
                key=f"user_symbol_{group}",
            )
            size = st.slider("Size (px)", 5, 40, cur_size, key=f"user_size_{group}")
            opacity = (
                st.slider(
                    "Opacity (%)",
                    10,
                    100,
                    int(cur_opacity * 100),
                    key=f"user_opacity_{group}",
                )
                / 100
            )
            color_map[group] = color
            symbol_map[group] = symbol
            size_map[group] = size
            opacity_map[group] = opacity
    return color_map, symbol_map, size_map, opacity_map
