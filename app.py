import streamlit as st
import pandas as pd
import plotly.express as px
import random
import copy
import colorsys
from typing import Dict, Any
from styles import build_style_maps, AVAILABLE_SYMBOLS   # отдельный файл

st.set_page_config(page_title="Geochem Explorer", layout="wide")

# ───────────────────────────────────────────────────────────────────
# DATA
# ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

df = load_csv(st.secrets["CSV_URL"])

df["type_loc"] = df["type"].astype(str) + "|" + df["Location"].astype(str)

# базовые карты из styles.py  → копии, которые можно править
base_color, base_symbol, base_size = build_style_maps(
    df, type_col="type", loc_col="Location"
)
color_map_user  = base_color.copy()
symbol_map_user = base_symbol.copy()
size_map_user   = base_size.copy()

# ───────────────────────────────────────────────────────────────────
# DEFAULT AXES
# ───────────────────────────────────────────────────────────────────
DEFAULT_X = "MgO"    if "MgO"    in df.columns else df.columns[0]
DEFAULT_Y = "d98Mo"  if "d98Mo"  in df.columns else df.columns[1]
DEFAULT_GROUP = "Location" if "Location" in df.columns else df.columns[1]

def axis_selector(label: str, default: str) -> str:
    mode_key, col_key = f"{label}_mode", f"{label}_col"
    st.session_state.setdefault(mode_key, "Column")
    st.session_state.setdefault(col_key, default)
    mode = st.sidebar.radio(f"{label} mode", ["Column", "Ratio"], key=mode_key)
    if mode == "Column":
        return st.sidebar.selectbox(
            f"{label} axis", df.columns, key=col_key,
            index=df.columns.get_loc(st.session_state[col_key])
        )
    num = st.sidebar.selectbox(f"{label} numerator", df.columns, key=f"{label}_num")
    den = st.sidebar.selectbox(f"{label} denominator", df.columns, key=f"{label}_den")
    ratio = f"{num}/{den}"
    if ratio not in df.columns:
        df[ratio] = df[num] / df[den]
    return ratio

x_axis = axis_selector("X", DEFAULT_X)
y_axis = axis_selector("Y", DEFAULT_Y)
log_x  = st.sidebar.checkbox("log X", key="log_x")
log_y  = st.sidebar.checkbox("log Y", key="log_y")

# ───────────────────────────────────────────────────────────────────
# SIDEBAR: per-group style editors
# ───────────────────────────────────────────────────────────────────
group_col = st.sidebar.selectbox(
    "Group by", df.columns, index=df.columns.get_loc(DEFAULT_GROUP)
)

styles: Dict[str, Dict[str, Any]] = {}    # собираем выбор пользователя
visible_groups = []

random.seed(42)
predefined_symbols = AVAILABLE_SYMBOLS.copy()

for g in sorted(df[group_col].dropna().unique()):
    key = str(g)

    with st.sidebar.expander(key, expanded=False):
        # текущие дефолты (из карт, а не из styles = может быть пусто)
        cur_color  = color_map_user.get(key,  "#1f77b4")
        cur_symbol = symbol_map_user.get(key, "circle")
        cur_size   = size_map_user.get(key,   20)

        show   = st.checkbox("Show", True, key=f"show_{g}")
        color  = st.color_picker("Color", cur_color,  key=f"col_{g}")
        symbol = st.selectbox("Symbol", predefined_symbols, index=predefined_symbols.index(cur_symbol), key=f"sym_{g}")
        size   = st.slider("Size (px)", 2, 40, cur_size, key=f"sz_{g}")
        alpha  = st.slider("Opacity (%)", 10, 100, 90, key=f"op_{g}") / 100
        outline_color = st.color_picker("Outline", "#000000", key=f"out_{g}")
        outline_width = st.slider("Outline width", 1.0, 6.0, 1.0, 0.5, key=f"ow_{g}")

        # 🔑  пользовательский выбор сразу записываем в рабочие карты
        color_map_user[key]  = color
        symbol_map_user[key] = symbol            # ok даже если key — Location
        size_map_user[key]   = size

        styles[key] = {
            "color": color, "symbol": symbol, "size": size,
            "opacity": alpha,
            "outline_color": outline_color,
            "outline_width": outline_width,
        }
        if show:
            visible_groups.append(g)

# ───────────────────────────────────────────────────────────────────
# DATA SUBSET
# ───────────────────────────────────────────────────────────────────
plot_df = df[df[group_col].isin(visible_groups)].copy()
size_col = "__marker_size"
plot_df[size_col] = plot_df["type"].map(size_map_user).fillna(20)

bg_color = "#ffffff"
font_color = "#000000"


df["type_loc"] = df["type"].astype(str) + "|" + df["Location"].astype(str)


# ───────────────────────────────────────────────────────────────────
# PLOT
# ───────────────────────────────────────────────────────────────────
fig = px.scatter(
    plot_df,
    x=x_axis, y=y_axis,
    color=plot_df["type_loc"].astype(str),          # оттенки по Location
    symbol=plot_df["type"].astype(str),             # фигура по Type
    size=plot_df[size_col],
    color_discrete_map = color_map_user,
    symbol_map=symbol_map_user,
    hover_name=group_col,
    log_x=log_x, log_y=log_y,
    height=650,
)

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



# convert chosen axis columns to numeric so Plotly treats them as continuous
for _col in [x_axis, y_axis]:
    if _col in df.columns:
        df[_col] = pd.to_numeric(df[_col], errors="coerce")

fig.update_traces(marker=dict(sizemode="diameter", sizeref=2.0, sizemin=2))

# применяем обводку и прозрачность
for tr in fig.data:
    loc = str(tr.name)                 # имя trace = Location
    st_dict = styles.get(loc, {})
    tr.marker.line.color = st_dict.get("outline_color", "#000")
    tr.marker.line.width = st_dict.get("outline_width", 1.0)
    tr.marker.opacity    = st_dict.get("opacity", 0.9)


st.plotly_chart(fig, use_container_width=True)

export_fig = copy.deepcopy(fig)
export_fig.update_layout(
    width=1200, height=800,
    margin=dict(l=80, r=120, t=60, b=60),   # +180 px справа
    showlegend=False,
)

# ── КНОПКИ СКАЧИВАНИЯ ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.download_button(
        "Save plot (PNG)",
        export_fig.to_image(format="png"),
        file_name="plot.png"
    )

with col2:
    st.download_button(
        "Save data (CSV)",
        plot_df.to_csv(index=False),
        file_name="data.csv"
    )

with col3:
    st.download_button(
        "Save plot (PDF)",
        export_fig.to_image(format="pdf"),
        file_name="plot.pdf",
        mime="application/pdf"
    )