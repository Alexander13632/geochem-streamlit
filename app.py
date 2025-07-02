import streamlit as st
import pandas as pd
import plotly.express as px
import copy
import random
from typing import Dict, Any
from styles import build_style_maps, AVAILABLE_SYMBOLS     # ваш файл
from utils import axis_selector


st.set_page_config(page_title="Geochem Explorer", layout="wide")

# ─── DATA ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

df = load_csv(st.secrets["CSV_URL"])

# двойной ключ сразу в датафрейм
df["type_loc"] = df["type"].astype(str) + "|" + df["Location"].astype(str)

# базовые карты из styles.py
base_color, base_symbol, base_size = build_style_maps(
    df, type_col="type", loc_col="Location"
)
color_map_user  = base_color.copy()   # ключ: type|loc
symbol_map_user = base_symbol.copy()  # ключ: type
size_map_user   = base_size.copy()    # ключ: type

# ─── AXES ──────────────────────────────────────────────────────────
DEFAULT_X, DEFAULT_Y = ("MgO", "d98Mo") if {"MgO", "d98Mo"} <= set(df.columns) \
                       else df.columns[:2]
DEFAULT_GROUP = "type_loc"            # важно!



x_axis = axis_selector(df, "X", DEFAULT_X)
y_axis = axis_selector(df, "Y", DEFAULT_Y)
log_x  = st.sidebar.checkbox("log X")
log_y  = st.sidebar.checkbox("log Y")

# ─── ГРУППЫ, ПОКАЗ/СКРЫТИЕ ────────────────────────────────────────
group_col = st.sidebar.selectbox(
    "Group by (for hover-labels)", df.columns,
    index=df.columns.get_loc(DEFAULT_GROUP)
)


plot_df = df.copy()

# ─── РЕДАКТОР ЦВЕТА (type|Location)  ───────────────────────────────
st.sidebar.markdown("---\n### Color & Trace style (type | Location)")
styles: Dict[str, Dict[str, Any]] = {}         # для контура / прозрачности
pre_symbols = AVAILABLE_SYMBOLS.copy()
random.seed(42)

for key in sorted(df["type_loc"].dropna().unique()):
    typ = key.split("|")[0]                    # часть до «|»
    with st.sidebar.expander(key, expanded=False):
        # дефолты
        cur_color  = color_map_user.get(key,  "#1f77b4")
        cur_symbol = symbol_map_user.get(typ, "circle")
        cur_size   = size_map_user.get(typ,   20)

        color  = st.color_picker("Color", cur_color, key=f"col_{key}")
        sym_idx = pre_symbols.index(cur_symbol) if cur_symbol in pre_symbols else 0
        symbol = st.selectbox("Symbol", pre_symbols, index=sym_idx, key=f"sym_{key}")
        size   = st.slider("Size (px)", 2, 40, cur_size, key=f"sz_{key}")
        alpha  = st.slider("Opacity (%)", 10, 100, 90, key=f"op_{key}") / 100
        outcol = st.color_picker("Outline", "#000000", key=f"out_{key}")
        outwid = st.slider("Outline width", 1.0, 6.0, 1.0, 0.5, key=f"ow_{key}")

        # обновляем рабочие карты
        color_map_user[key]      = color
        symbol_map_user[typ]     = symbol     # символ по type!
        size_map_user[typ]       = size

        styles[key] = {
            "opacity": alpha,
            "outline_color": outcol,
            "outline_width": outwid,
        }

# столбец размеров для Plotly (по type)
size_col = "__marker_size"
plot_df[size_col] = plot_df["type"].map(size_map_user).fillna(20)

bg_color = "#ffffff"
font_color = "#000000"

# ─── PLOT ──────────────────────────────────────────────────────────
fig = px.scatter(
    plot_df,
    x=x_axis, y=y_axis,
    color=plot_df["type_loc"].astype(str),
    symbol=plot_df["type"].astype(str),
    size=plot_df[size_col],
    color_discrete_map=color_map_user,
    symbol_map=symbol_map_user,
    hover_name=group_col,
    log_x=log_x, log_y=log_y,
    height=650,
)

# обводка / прозрачность из styles
for tr in fig.data:
    st_dict = styles.get(tr.name, {})
    tr.marker.line.color = st_dict.get("outline_color", "#000")
    tr.marker.line.width = st_dict.get("outline_width", 1.0)
    tr.marker.opacity    = st_dict.get("opacity", 0.9)

fig.update_traces(marker=dict(sizemode="diameter", sizeref=2.0, sizemin=2))

# лаконичный формат осей + фоны (можно оставить ваш прежний блок)
fig.update_layout(
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    legend=dict(
        font=dict(color=font_color)
    ),
    font=dict(color=font_color),
)


fig.update_xaxes(
    title_font=dict(color=font_color),
    tickfont=dict(color=font_color),
    linecolor=font_color,
    gridcolor="rgba(0,0,0,0.12)",
    zerolinecolor=font_color
)
fig.update_yaxes(
    title_font=dict(color=font_color),
    tickfont=dict(color=font_color),
    linecolor=font_color,
    gridcolor="rgba(0,0,0,0.12)",
    zerolinecolor=font_color
)

# ▸ сразу после fig = px.scatter(...)  (или после update_layout)

axis_style = dict(
    linecolor="#000000",          # основная линия оси
    mirror=True, showline=True,   # рисовать «рамку»
    ticks="inside",               # насечки внутрь поля
    ticklen=6,                    # длина насечки, px
    tickwidth=1,                  # толщина линии
    tickcolor="#000000",          # цвет насечки
    gridcolor="rgba(0,0,0,0.15)",     # крупная сетка
    minor_showgrid=True,
    minor_gridwidth=0.5,
    minor_gridcolor="rgba(0,0,0,0.05)",
)

fig.update_xaxes(**axis_style)
fig.update_yaxes(**axis_style)

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
