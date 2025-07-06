import streamlit as st
import json
import pandas as pd
import plotly.express as px
import copy
import random
from typing import Dict, Any
from styles import build_style_maps, AVAILABLE_SYMBOLS     # ваш файл
from utils import axis_selector
from plotting import plot_demo_table, plot_user_table, plot_box_plot
from data_loader import get_dataframe
from user_style import generate_group_styles, group_style_editor
from binning import binning_widget
from save_style_to_json import export_style
from editors import inherit_styles_from_typeloc

st.set_page_config(page_title="Geochem Explorer", layout="wide")



# ─── DATA ──────────────────────────────────────────────────────────
df, user_data = get_dataframe()

columns = list(df.columns)

# JSON
uploaded_style = st.sidebar.file_uploader("Загрузить стиль (JSON)", type=["json"], key="style_file")
styles: Dict[str, Dict[str, Any]] = {}               # <<< NEW >>>  инициализируем один раз



# ─── SIDEBAR ──────────────────────────────────────────────────────
plot_type = st.sidebar.selectbox(
    "Plot type",
    ["Scatter plot", "Box plot"],   # можно будет добавить другие типы позже
    index=0
)


# --- Если есть колонки "type" и "Location" ---
if "type" in df.columns and "Location" in df.columns:
    df["type_loc"] = df["type"].astype(str) + "|" + df["Location"].astype(str)
    base_color, base_symbol, base_size = build_style_maps(
        df, type_col="type", loc_col="Location"
    )
    color_map_user  = base_color.copy()
    symbol_map_user = base_symbol.copy()
    size_map_user   = base_size.copy()
else:
    df["type_loc"] = ""
    color_map_user  = {}
    symbol_map_user = {}
    size_map_user   = {}

# --- Селекторы осей и группировки ---
if user_data:
    # Для пользовательских данных селекторы пустые (выбор только вручную)
    x_axis = st.sidebar.selectbox("Axis X", [""] + columns, index=0)
    y_axis = st.sidebar.selectbox("Axis Y", [""] + columns, index=0)
    group_col = st.sidebar.selectbox("Grouping variable", [""] + columns, index=0)
else:
    # Для дефолтных данных — как было!
    default_x = "MgO" if "MgO" in columns else (columns[0] if columns else "")
    default_y = "d98Mo" if "d98Mo" in columns else (columns[1] if len(columns) > 1 else "")
    default_group = "type_loc" if "type_loc" in columns else ""
    x_axis = st.sidebar.selectbox("Axis X", columns, index=columns.index(default_x) if default_x in columns else 0)
    y_axis = st.sidebar.selectbox("Axis Y", columns, index=columns.index(default_y) if default_y in columns else 0)
    group_col = st.sidebar.selectbox("Grouping variable", [""] + columns, index=([""] + columns).index(default_group) if default_group in columns else 0)

log_x  = st.sidebar.checkbox("log X")
log_y  = st.sidebar.checkbox("log Y")

bin_col, bin_labels = binning_widget(df, group_col)
if bin_col:
    group_for_plot = bin_col
else:
    group_for_plot = group_col



if not x_axis or not y_axis:
    st.warning("Please select both X and Y axes to plot.")
    st.stop()

plot_df = df.copy()
bg_color = "#ffffff"
font_color = "#000000"



# ─── СБОР СТИЛЕЙ ДЛЯ ВЫБРАННОЙ ГРУППЫ ────────────────────────────
def build_group_style(df, group_for_plot,
                      base_color, base_symbol, base_size):
    """Карта стилей для любой группировки."""
    if group_for_plot == "type_loc":
        # используем уже готовые карты
        return base_color.copy(), base_symbol.copy(), base_size.copy()
    # иначе наследуем из type|Location
    return inherit_styles_from_typeloc(
        df, group_for_plot,
        base_color, base_symbol, base_size
    )

# ---------- универсальный блок ----------
if group_for_plot:                   # выбран столбец группировки
    color_map_user, symbol_map_user, size_map_user = build_group_style(
        df, group_for_plot,
        base_color, base_symbol, base_size
    )
    opacity_map_user = {g: 0.9 for g in color_map_user}

    st.sidebar.markdown(f"---\n### Color & Trace style ({group_for_plot})")
    color_map_user, symbol_map_user, size_map_user, opacity_map_user = group_style_editor(
        list(color_map_user.keys()),
        color_map_user, symbol_map_user,
        size_map_user, opacity_map_user
    )

    styles = {
        g: {
            "color"  : color_map_user[g],
            "symbol" : symbol_map_user[g],
            "size"   : size_map_user[g],
            "opacity": opacity_map_user[g],
        }
        for g in color_map_user
    }
else:
    styles = {}




if not user_data:
    st.sidebar.markdown("---\n### Color & Trace style (type | Location)")
    
    pre_symbols = AVAILABLE_SYMBOLS.copy()
    random.seed(42)
    for key in sorted(df["type_loc"].dropna().unique()):
        typ = key.split("|")[0]
        with st.sidebar.expander(key, expanded=False):
            cur_color  = color_map_user.get(key,  "#1f77b4")
            cur_symbol = symbol_map_user.get(typ, "circle")
            cur_size   = size_map_user.get(typ,   20)
            # Вот здесь меняешь ключи!
            color  = st.color_picker("Color", cur_color, key=f"demo_col_{key}")
            sym_idx = pre_symbols.index(cur_symbol) if cur_symbol in pre_symbols else 0
            symbol = st.selectbox("Symbol", pre_symbols, index=sym_idx, key=f"demo_sym_{key}")
            size   = st.slider("Size (px)", 2, 80, cur_size, key=f"demo_sz_{key}")
            alpha  = st.slider("Opacity (%)", 10, 100, 90, key=f"demo_op_{key}") / 100
            outcol = st.color_picker("Outline", "#000000", key=f"demo_out_{key}")
            outwid = st.slider("Outline width", 1.0, 6.0, 1.0, 0.5, key=f"demo_ow_{key}")

            color_map_user[key]      = color
            symbol_map_user[typ]     = symbol
            size_map_user[typ]       = size
            styles[key] = {
                "color"        : color,
                "symbol"       : symbol,
                "size"         : size,
                "opacity"      : alpha,
                "outline_color": outcol,
                "outline_width": outwid,
            }


opacity_map_user = {}   # <- чтобы был всегда, даже если не user_data

# ─── ЗАГРУЗКА ФАЙЛА ─────────────────────────────────────────────
if uploaded_style is not None:
    try:
        styles = json.load(uploaded_style)          # файл-объект -> dict

        # --- ⬇︎ РАСПАРСИВАЕМ И ПРИМЕНЯЕМ СТИЛИ ------------------
        for key, attrs in styles.items():
            # ☐ Цвет (ключ — всегда полный «type|Location» или имя группы)
            if "color" in attrs:
                color_map_user[key] = attrs["color"]

            # ☐ Символ / размер: для демо-режима берём только «type»
            typ = key.split("|")[0] if not user_data else key
            if "symbol" in attrs:
                symbol_map_user[typ] = attrs["symbol"]
            if "size" in attrs:
                size_map_user[typ] = attrs["size"]

            # ☐ Прозрачность
            if "opacity" in attrs:
                opacity_map_user[key] = attrs["opacity"]
        # ---------------------------------------------------------

        st.success("Стиль загружен!")
    except Exception as e:
        st.error(f"Не удалось загрузить стиль: {e}")



# ─── КНОПКА «СОХРАНИТЬ» ─────────────────────────────────────────
json_bytes = json.dumps(styles, indent=2).encode("utf-8")
st.sidebar.download_button(
    "💾 Сохранить стиль (JSON)",
    data=json_bytes,
    file_name="style.json",
    mime="application/json",
    use_container_width=True,
)




if plot_type == "Scatter plot":
    if not user_data:
        fig = plot_demo_table(
            df=plot_df,
            x_axis=x_axis, y_axis=y_axis,
            group_for_plot=group_for_plot,
            color_map_user=color_map_user,
            symbol_map_user=symbol_map_user,
            size_map_user=size_map_user,
            log_x=log_x, log_y=log_y,
            styles=styles,
            bg_color=bg_color, font_color=font_color
        )
    else:
        fig = plot_user_table(
            df=plot_df,
            x_axis=x_axis, y_axis=y_axis,
            group_for_plot=group_for_plot,
            color_map_user=color_map_user,
            symbol_map_user=symbol_map_user,
            size_map_user=size_map_user,
            log_x=log_x, log_y=log_y,
            styles=styles,
            bg_color=bg_color, font_color=font_color
        )
elif plot_type == "Box plot":
    # Группировка нужна обязательно!
    if group_for_plot and group_for_plot in plot_df.columns:
        fig = plot_box_plot(
            df=plot_df,
            x="type_loc", y=y_axis,
            color="type_loc",
            color_map = color_map_user,
            bg_color=bg_color, font_color=font_color
        )
    else:
        st.warning("Please select a grouping variable to build a box plot.")
        st.stop()
else:
    st.warning("Unknown plot type selected.")
    st.stop()

st.plotly_chart(fig, use_container_width=True)



# ─── DOWNLOADS ─────────────────────────────────────────────────────
export_fig = copy.deepcopy(fig)
export_fig.update_layout(width=1200, height=800,
                         margin=dict(l=80, r=120, t=60, b=60),
                         showlegend=False)

col1, col2, col3 = st.columns(3)
with col1:
    st.download_button("Save plot (PNG)",
        export_fig.to_image(format="png"), file_name="plot.png")
with col2:
    st.download_button("Save data (CSV)",
        plot_df.to_csv(index=False), file_name="data.csv")
with col3:
    st.download_button("Save plot (PDF)",
        export_fig.to_image(format="pdf"), file_name="plot.pdf",
        mime="application/pdf")
