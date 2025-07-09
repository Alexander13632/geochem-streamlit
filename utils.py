import streamlit as st
import pandas as pd

def axis_selector(df: pd.DataFrame, label: str, default: str) -> str:
    mode_key, col_key = f"{label}_mode", f"{label}_col"
    st.session_state.setdefault(mode_key, "Column")
    st.session_state.setdefault(col_key, default)

    mode = st.sidebar.radio(f"{label} mode", ["Column", "Ratio"], key=mode_key)
    if mode == "Column":
        return st.sidebar.selectbox(
            f"{label} axis", df.columns, key=col_key
        )

    # Режим Ratio: делаем выпадающие списки с пустым значением
    num_options = [""] + list(df.columns)
    den_options = [""] + list(df.columns)
    num = st.sidebar.selectbox(f"{label} numerator", num_options, key=f"{label}_num")
    den = st.sidebar.selectbox(f"{label} denominator", den_options, key=f"{label}_den")

    if not num or not den:
        st.sidebar.warning("Please select numerator and denominator")
        return ""  # Не возвращаем ничего, если не выбрано

    ratio = f"{num}/{den}"
    if ratio not in df.columns:
        try:
            df[ratio] = df[num] / df[den]
        except Exception as e:
            st.sidebar.error(f"Error calculating ratio: {e}")
            return ""
    return ratio