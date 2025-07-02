import streamlit as st
import pandas as pd

def axis_selector(df: pd.DataFrame, label: str, default: str) -> str:
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