import streamlit as st
import json
import pandas as pd
import copy
import random
import normalizer
from typing import Dict, Any
from styles import build_style_maps, line_style_editor, AVAILABLE_SYMBOLS  # ваш файл
from utils import axis_selector
from plotting import plot_demo_table, plot_user_table, plot_box_plot
from data_loader import get_dataframe
from user_style import generate_group_styles, group_style_editor
from binning import binning_widget
from editors import inherit_styles_from_typeloc
from filter_bar import filter_dataframe
from sidebar_info import show_sidebar_info
from tas_plot import show_tas
from export_manager import render_export_buttons, render_export_settings


show_sidebar_info()
st.set_page_config(page_title="GeoQuick", layout="wide")


# ─── DATA ──────────────────────────────────────────────────────────
df, user_data = get_dataframe()

columns = list(df.columns)


if {"type", "Location"}.issubset(df.columns):
    df["type_loc"] = df["type"].astype(str) + "|" + df["Location"].astype(str)
    base_color, base_symbol, base_size = build_style_maps(
        df, type_col="type", loc_col="Location"
    )
else:
    df["type_loc"] = ""
    base_color, base_symbol, base_size = {}, {}, {}

color_map_user = base_color.copy()
symbol_map_user = base_symbol.copy()
size_map_user = base_size.copy()

# JSON
uploaded_style = st.sidebar.file_uploader(
    "Upload style (JSON)", type=["json"], key="style_file"
)
styles: Dict[str, Dict[str, Any]] = {}  # <<< NEW >>>  initialization one time


# ─── SIDEBAR ──────────────────────────────────────────────────────
plot_type = st.sidebar.selectbox(
    "Plot type",
    [
        "Scatter plot",
        "Box plot",
        "TAS diagram",
        "Multielemental plot",
    ],  # add different plot types here later
    index=0,
)


st.sidebar.markdown("### Tooltip columns")
# default set if this set exist
hard_defaults = ["MgO", "d98Mo"]
# оставляем только те, что присутствуют в текущем DataFrame
default_hover = [c for c in hard_defaults if c in df.columns]
hover_cols = st.sidebar.multiselect(
    "Show in tooltip",
    options=list(df.columns),
    default=default_hover,  # ← empty list if none found
    key="hover_cols",
)

hover_cols = hover_cols or []  # if nothing is selected, then an empty list


# ─── СБОР СТИЛЕЙ ДЛЯ ВЫБРАННОЙ ГРУППЫ ────────────────────────────
def build_group_style(df, group_for_plot, base_color, base_symbol, base_size):
    """Возвращает карты стилей для любой группировки.

    • если в датафрейме есть type+Location → наследуем;
    • иначе генерируем новые карты для выбранной группы."""
    have_typeloc = {"type", "Location"}.issubset(df.columns)

    # ── 1. default case, as before ──────────────────────────
    if group_for_plot == "type_loc" and have_typeloc:
        return base_color.copy(), base_symbol.copy(), base_size.copy()

    # ── 2. can we inherit from type|Location? ───────────────────
    if have_typeloc:
        return inherit_styles_from_typeloc(
            df, group_for_plot, base_color, base_symbol, base_size
        )

    # ── 3. no type/Location → create new styles  -------------
    #     (color, symbol, size)
    colors, symbols = generate_group_styles(df[group_for_plot].dropna().unique())
    sizes = {g: 10 for g in colors}  # все по 10 px
    return colors, symbols, sizes


# --------------------------------------------------------------
#   MULTIELEMENTAL  PLOT
# --------------------------------------------------------------
if plot_type == "Multielemental plot":
    fig = None
    group_col: str | None = None
    elems: list[str] = []
    norm_set: dict[str, float] | None = None

    # 1. селектор группы
    group_choice = st.sidebar.selectbox(
        "Grouping variable", [""] + list(df.columns), index=0
    )
    group_col = group_choice or None

    # 2. выбор элементов / норм-набора
    elems, norm_set = normalizer.norm_controls(df)

    # ... выбор group_col, elems, norm_set ...

    if elems and norm_set:
        df_plot = df.copy()
        if group_col:
            df_plot = df_plot[df_plot[group_col].notna()]

            color_map, symbol_map, size_map = build_group_style(
                df_plot, group_col, base_color, base_symbol, base_size
            )
            opacity_map = {g: 0.9 for g in color_map}
            width_map = {g: 2 for g in color_map}
            dash_map = {g: "solid" for g in color_map}
            line_color_map = {g: color_map[g] for g in color_map}  # стартуем тем же
            outline_color_map = {g: "#000000" for g in color_map}  # черный контур
            outline_width_map = {g: 0 for g in color_map}

            st.sidebar.markdown(f"---\n### Line & Marker style ({group_col})")
            (
                color_map,
                symbol_map,
                size_map,
                opacity_map,
                width_map,
                dash_map,
                line_color_map,
                outline_color_map,
                outline_width_map,
            ) = line_style_editor(
                list(color_map.keys()),
                color_map,
                symbol_map,
                size_map,  # 1-3
                opacity_map,
                width_map,
                dash_map,  # 4-6
                line_color_map,  # 7
                outline_color_map,
                outline_width_map,  # 8-9
            )
        else:
            color_map = symbol_map = size_map = opacity_map = None
            width_map = dash_map = line_color_map = outline_color_map = (
                outline_width_map
            ) = None

        fig = normalizer.multielemental_plot(
            df_plot,
            elems,
            norm_set,
            group_col=group_col,
            color_map=color_map,
            symbol_map=symbol_map,
            size_map=size_map,
            width_map=width_map,
            dash_map=dash_map,
            line_color_map=line_color_map,
            outline_color_map=outline_color_map,
            outline_width_map=outline_width_map,
            log_y=True,
        )
        st.plotly_chart(fig, use_container_width=True, key="multielemental_chart")
        if fig is not None:
            st.markdown("---")
            export_config = render_export_settings()
            render_export_buttons(fig, export_config, "export_multielemental")
    st.stop()


if plot_type == "TAS diagram":
    fig, plot_df_tas = show_tas(
        df=df,
        user_data=user_data,
        base_color=base_color,
        base_symbol=base_symbol,
        base_size=base_size,
        build_group_style=build_group_style,
        group_style_editor=group_style_editor,
        filter_dataframe=filter_dataframe,
        hover_cols=hover_cols,
    )
    
    # Экспорт для TAS диаграммы
    st.markdown("---")
    export_config = render_export_settings()
    render_export_buttons(fig, export_config, "export_tas")
    st.stop()


# --- Selectors for axes and grouping ---
if user_data:
    # for user data — only manual axis selection
    x_axis = axis_selector(df, "X", default=columns[0])
    y_axis = axis_selector(
        df, "Y", default=columns[1] if len(columns) > 1 else columns[0]
    )
    group_col = st.sidebar.selectbox("Grouping variable", [""] + columns, index=0)
else:
    # for default data — can set defaults
    default_x = "MgO" if "MgO" in columns else (columns[0] if columns else "")
    default_y = (
        "SiO2" if "SiO2" in columns else (columns[1] if len(columns) > 1 else "")
    )
    default_group = "type_loc" if "type_loc" in columns else ""
    x_axis = axis_selector(df, "X", default=default_x)
    y_axis = axis_selector(df, "Y", default=default_y)
    group_col = st.sidebar.selectbox(
        "Grouping variable",
        [""] + columns,
        index=([""] + columns).index(default_group) if default_group in columns else 0,
    )

log_x = st.sidebar.checkbox("log X")
log_y = st.sidebar.checkbox("log Y")

bin_col, bin_labels = None, None

nested_bin_col = None  # конечная комбинированная колонка
second_num_col = None  # числовая переменная для бинов


if group_col and not pd.api.types.is_numeric_dtype(df[group_col]):
    # есть ли вообще числовые столбцы?
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if numeric_cols:
        second_num_col = st.sidebar.selectbox(
            "Sub-bin by numeric …", [""] + numeric_cols, index=0
        )

        if second_num_col:
            # общий бининг для всей таблицы (те же интервалы во всех группах)
            sub_bin_col, _ = binning_widget(df, second_num_col)

            if sub_bin_col:
                combined = df[group_col].astype(str) + "|" + df[sub_bin_col].astype(str)
                nested_bin_col = "__combined_group"
                df[nested_bin_col] = combined

if nested_bin_col:  # вариант «категория + бины»
    group_for_plot = nested_bin_col

elif group_col and pd.api.types.is_numeric_dtype(df[group_col]):
    # старая логика «числовая группировка → глобальный бининг»
    global_bin_col, _ = binning_widget(df, group_col)
    group_for_plot = global_bin_col if global_bin_col else None

else:
    group_for_plot = group_col or None  # просто категориальная


if not x_axis or not y_axis:
    st.warning("Please select both X and Y axes to plot.")
    st.stop()

df = filter_dataframe(df)


plot_df = df.copy()
bg_color = "#ffffff"
font_color = "#000000"


# ---------- универсальный блок ----------
if group_for_plot:
    df = df[df[group_for_plot].notna()]  # выбран столбец группировки
    color_map_user, symbol_map_user, size_map_user = build_group_style(
        df, group_for_plot, base_color, base_symbol, base_size
    )
    opacity_map_user = {g: 0.9 for g in color_map_user}

    st.sidebar.markdown(f"---\n### Color & Trace style ({group_for_plot})")
    color_map_user, symbol_map_user, size_map_user, opacity_map_user = (
        group_style_editor(
            list(color_map_user.keys()),
            color_map_user,
            symbol_map_user,
            size_map_user,
            opacity_map_user,
        )
    )

    styles = {
        g: {
            "color": color_map_user[g],
            "symbol": symbol_map_user[g],
            "size": size_map_user[g],
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
            cur_color = color_map_user.get(key, "#1f77b4")
            cur_symbol = symbol_map_user.get(typ, "circle")
            cur_size = size_map_user.get(typ, 20)
            color = st.color_picker("Color", cur_color, key=f"demo_col_{key}")
            sym_idx = pre_symbols.index(cur_symbol) if cur_symbol in pre_symbols else 0
            symbol = st.selectbox(
                "Symbol", pre_symbols, index=sym_idx, key=f"demo_sym_{key}"
            )
            size = st.slider("Size (px)", 2, 80, cur_size, key=f"demo_sz_{key}")
            alpha = st.slider("Opacity (%)", 10, 100, 90, key=f"demo_op_{key}") / 100
            outcol = st.color_picker("Outline", "#000000", key=f"demo_out_{key}")
            outwid = st.slider(
                "Outline width", 1.0, 6.0, 1.0, 0.5, key=f"demo_ow_{key}"
            )

            color_map_user[key] = color
            symbol_map_user[typ] = symbol
            size_map_user[typ] = size
            styles[key] = {
                "color": color,
                "symbol": symbol,
                "size": size,
                "opacity": alpha,
                "outline_color": outcol,
                "outline_width": outwid,
            }


opacity_map_user = {}  # <- чтобы был всегда, даже если не user_data

# ─── download data ─────────────────────────────────────────────
if uploaded_style is not None:
    try:
        styles = json.load(uploaded_style)  # file-object -> dict

        # --- ⬇︎ PARSE AND APPLY STYLES ------------------
        for key, attrs in styles.items():
            # ☐ Color (key — always full «type|Location» or group name)
            if "color" in attrs:
                color_map_user[key] = attrs["color"]

            # ☐ Symbol / size: for demo mode we take only «type»
            typ = key.split("|")[0] if not user_data else key
            if "symbol" in attrs:
                symbol_map_user[typ] = attrs["symbol"]
            if "size" in attrs:
                size_map_user[typ] = attrs["size"]

            # ☐ Opacity
            if "opacity" in attrs:
                opacity_map_user[key] = attrs["opacity"]
        # ---------------------------------------------------------

        st.success("Style loaded successfully!")
    except Exception as e:
        st.error(f"Failed to load style: {e}")


# ─── SAVE BUTTON ─────────────────────────────────────────
json_bytes = json.dumps(styles, indent=2).encode("utf-8")
st.sidebar.download_button(
    "💾 Save style (JSON)",
    data=json_bytes,
    file_name="style.json",
    mime="application/json",
    use_container_width=True,
)


if plot_type == "Scatter plot":
    if not user_data:
        fig = plot_demo_table(
            df=plot_df,
            x_axis=x_axis,
            y_axis=y_axis,
            group_for_plot=group_for_plot,
            color_map_user=color_map_user,
            symbol_map_user=symbol_map_user,
            size_map_user=size_map_user,
            log_x=log_x,
            log_y=log_y,
            styles=styles,
            bg_color=bg_color,
            font_color=font_color,
            hover_cols=hover_cols,
        )

    else:
        fig = plot_user_table(
            df=plot_df,
            x_axis=x_axis,
            y_axis=y_axis,
            group_for_plot=group_for_plot,
            color_map_user=color_map_user,
            symbol_map_user=symbol_map_user,
            size_map_user=size_map_user,
            log_x=log_x,
            log_y=log_y,
            styles=styles,
            bg_color=bg_color,
            font_color=font_color,
            hover_cols=hover_cols,
        )
elif plot_type == "Box plot":
    # Группировка нужна обязательно!
    if group_for_plot and group_for_plot in plot_df.columns:
        fig = plot_box_plot(
            df=plot_df,
            x=group_for_plot,
            y=y_axis,
            color=group_for_plot,
            color_map=color_map_user,
            bg_color=bg_color,
            font_color=font_color,
            hover_cols=hover_cols,
        )
    else:
        st.warning("Please select a grouping variable to build a box plot.")
        st.stop()


    if 'fig' in locals() and fig is not None:
        st.markdown("---")
        export_config = render_export_settings()
        export_key_prefix = f"export_{plot_type.lower().replace(' ', '_')}"
        render_export_buttons(fig, export_config, export_key_prefix)

else:
    st.warning("Unknown plot type selected.")
    st.stop()


st.plotly_chart(fig, use_container_width=True)


# ─── DOWNLOADS ─────────────────────────────────────────────────────
export_fig = copy.deepcopy(fig)
export_fig.update_layout(
    width=1200, height=800, margin=dict(l=80, r=120, t=60, b=60), showlegend=False
)

# ─── UNIVERSAL EXPORT SECTION ─────────────────────────────────────────
# Эта секция будет работать для всех типов графиков
if 'fig' in locals() and fig is not None:
    st.markdown("---")
    
    # Render export settings
    export_config = render_export_settings()
    
    # Render export buttons
    export_key_prefix = f"export_{plot_type.lower().replace(' ', '_')}"
    render_export_buttons(fig, export_config, export_key_prefix)