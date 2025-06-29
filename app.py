import streamlit as st
import pandas as pd
import plotly.express as px
import random
from typing import Dict, Any

st.set_page_config(page_title="Geochem Explorer", layout="wide")

# ------------------------------------------------------------------
# DATA LOADING WITH CACHING
# ------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

CSV_URL = st.secrets["CSV_URL"]
df = load_csv(CSV_URL)

# ------------------------------------------------------------------
# DEFAULTS • d98Mo vs MgO • group → type
# ------------------------------------------------------------------
DEFAULT_X = "MgO" if "MgO" in df.columns else df.columns[0]
DEFAULT_Y = "d98Mo" if "d98Mo" in df.columns else df.columns[1]
DEFAULT_GROUP = "type" if "type" in df.columns else df.columns[-1]

# ------------------------------------------------------------------
# AXIS SELECTOR UTIL
# ------------------------------------------------------------------

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

log_x = st.sidebar.checkbox("log X", key="log_x")
log_y = st.sidebar.checkbox("log Y", key="log_y")

# ------------------------------------------------------------------
# GROUPING & STYLE CONTROLS
# ------------------------------------------------------------------

group_col = st.sidebar.selectbox(
    "Group by", df.columns, index=df.columns.get_loc(DEFAULT_GROUP), key="group_by"
)

random.seed(42)
predefined_symbols = [
    "circle", "square", "diamond", "triangle-up", "cross", "x",
    "triangle-down", "star"
]

styles: Dict[Any, Dict[str, Any]] = {}
visible_groups = []
for idx, g in enumerate(sorted(df[group_col].dropna().unique())):
    group_str = str(g)  # ВАЖНО: всегда строка!

    colour_key, symbol_key = f"c_{g}", f"s_{g}"
    st.session_state.setdefault(colour_key, f"#{random.randint(0, 0xFFFFFF):06x}")
    st.session_state.setdefault(symbol_key, predefined_symbols[idx % len(predefined_symbols)])

    with st.sidebar.expander(group_str, expanded=False):
        show = st.checkbox("Show", True, key=f"show_{g}")
        color = st.color_picker("Color", st.session_state[colour_key], key=colour_key)
        symbol = st.selectbox("Symbol", predefined_symbols, key=symbol_key,
                              index=predefined_symbols.index(st.session_state[symbol_key]))
        size = st.slider("Size (px)", 2, 40, 20, key=f"sz_{g}")
        alpha = st.slider("Opacity (%)", 10, 100, 90, key=f"op_{g}") / 100.0
        outline_color = st.color_picker("Outline color", "#000000", key=f"outline_{g}")
        outline_width = st.slider(
            "Outline width", min_value=0.1, max_value=6.0, value=0.2, step=0.1, key=f"ow_{g}"
        )
        styles[group_str] = {  # ключ — строка!
            "color": color,
            "symbol": symbol,
            "size": size,
            "opacity": alpha,
            "outline_color": outline_color,
            "outline_width": outline_width,
        }
        if show:
            visible_groups.append(g)

plot_df = df[df[group_col].isin(visible_groups)].copy()
size_col = "__marker_size"
plot_df[size_col] = plot_df[group_col].map(lambda v: styles.get(v, {}).get("size", 10))

# ------------------------------------------------------------------
# PLOTLY SIZE HANDLING (absolute pixel diameters)
# ------------------------------------------------------------------
max_size = plot_df[size_col].max() if not plot_df.empty else 10
sizeref = 2.0  # diameter mode: pixel ≈ value / (sizeref/2)

# ------------------------------------------------------------------

bg_color = "#ffffff"
font_color = "#000000"
# SCATTER PLOT
# ------------------------------------------------------------------
fig = px.scatter(
    plot_df,
    x=x_axis,
    y=y_axis,
    color=plot_df[group_col].astype(str),
    symbol=plot_df[group_col].astype(str),
    size=size_col,
    size_max=max_size,
    color_discrete_map={g: s["color"] for g, s in styles.items()},
    symbol_map={g: s["symbol"] for g, s in styles.items()},
    hover_name=group_col,
    log_x=log_x,
    log_y=log_y,
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

# convert chosen axis columns to numeric so Plotly treats them as continuous
for _col in [x_axis, y_axis]:
    if _col in df.columns:
        df[_col] = pd.to_numeric(df[_col], errors="coerce")


fig.update_traces(marker=dict(sizemode="diameter", sizeref=sizeref, sizemin=2))

# Apply per‑trace opacity
for trace in fig.data:
    group_name = str(trace.name)
    if group_name in styles:
        trace.update(marker=dict(
            opacity=styles[group_name]["opacity"],
            line=dict(
                color=styles[group_name]["outline_color"],
                width=styles[group_name]["outline_width"],
            )
        ))


# ------------------------------------------------------------------
# AXIS STYLING (fonts + grid + inside ticks)
# ------------------------------------------------------------------
axis_title_font = dict(size=18, family="Arial")
axis_tick_font = dict(size=14)
for update in (fig.update_xaxes, fig.update_yaxes):
    update(
        title_font=axis_title_font,
        tickfont=axis_tick_font,
        ticks="inside", ticklen=4,
        showline=True, linecolor="black", mirror=True,
        showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.12)",
        minor_showgrid=True, minor_gridwidth=0.5, minor_gridcolor="rgba(0,0,0,0.04)",
    )

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# DOWNLOAD BUTTONS
# ------------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    st.download_button("Save plot (PNG)", fig.to_image(format="png"), "plot.png")
with col2:
    st.download_button("Save data (CSV)", plot_df.to_csv(index=False), "data.csv")