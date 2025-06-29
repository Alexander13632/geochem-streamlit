import streamlit as st, pandas as pd, plotly.express as px

st.set_page_config(page_title="Geochem Explorer", layout="wide")

@st.cache_data(ttl=3600)
def load(url: str):
    return pd.read_csv(url)

df = load(st.secrets["CSV_URL"])

mode = st.sidebar.radio("Select X / Y", ["Column", "Ratio"])
if mode == "Column":
    x = st.sidebar.selectbox("X axis", df.columns)
    y = st.sidebar.selectbox("Y axis", df.columns)
else:
    num = st.sidebar.selectbox("Numerator", df.columns)
    den = st.sidebar.selectbox("Denominator", df.columns)
    ratio = f"{num}/{den}"
    df[ratio] = df[num] / df[den]
    x = ratio
    y = st.sidebar.selectbox("Y axis", df.columns)

group = st.sidebar.selectbox("Group by", df.columns)
log_x = st.sidebar.checkbox("log X")
log_y = st.sidebar.checkbox("log Y")

styles = {}
for g in sorted(df[group].dropna().unique()):
    with st.sidebar.expander(str(g)):
        styles[g] = {
            "color": st.color_picker("Color", "#1f77b4", key=f"c{g}"),
            "symbol": st.selectbox("Symbol",
                ["circle", "square", "diamond", "triangle-up", "cross", "x"],
                key=f"s{g}")
        }

fig = px.scatter(
    df, x=x, y=y,
    color=df[group].astype(str),
    symbol=df[group].astype(str),
    color_discrete_map={g: s["color"] for g, s in styles.items()},
    symbol_map={g: s["symbol"] for g, s in styles.items()},
    hover_name=group,
    log_x=log_x, log_y=log_y,
    height=650,
)
st.plotly_chart(fig, use_container_width=True)
st.download_button("Save plot (PNG)", fig.to_image(format="png"), "plot.png")
st.download_button("Save data (CSV)", df.to_csv(index=False), "data.csv")

