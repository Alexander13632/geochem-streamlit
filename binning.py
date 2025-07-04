import pandas as pd
import streamlit as st

def binning_widget(df: pd.DataFrame, group_col: str):
    """
    Widget for manual/automatic binning of a numeric variable into intervals (bins).
    Returns: (name of the new column for bins or None, list of strings with bin labels or None)
    """
    bins_col = None
    bin_labels = None

    if group_col and pd.api.types.is_numeric_dtype(df[group_col]):
        st.sidebar.markdown("### Binning for grouping")
        mode = st.sidebar.radio(
            "Binning mode", ["Equal width", "Manual"], horizontal=True, key="bin_mode"
        )
        if mode == "Equal width":
            n_bins = st.sidebar.slider("Number of bins", 2, 15, 4, key="bin_nbins")
            bin_col = f"{group_col}_bin"
            df[bin_col], bin_edges = pd.cut(df[group_col], bins=n_bins, retbins=True, include_lowest=True)
            bins_col = bin_col
            bin_labels = [f"{round(left, 2)}–{round(right, 2)}" for left, right in zip(bin_edges[:-1], bin_edges[1:])]
        elif mode == "Manual":
            min_val, max_val = float(df[group_col].min()), float(df[group_col].max())
            bins_str = st.sidebar.text_input(
                "Enter bin edges (comma-separated)", 
                value=f"{min_val:.2f},{max_val:.2f}",
                key="bin_edges"
            )
            try:
                edges = [float(x.strip()) for x in bins_str.split(",") if x.strip() != ""]
                if len(edges) >= 2:
                    bin_col = f"{group_col}_bin"
                    df[bin_col] = pd.cut(df[group_col], bins=edges, include_lowest=True)
                    bins_col = bin_col
                    bin_labels = [f"{edges[i]}–{edges[i+1]}" for i in range(len(edges)-1)]
            except Exception as e:
                st.sidebar.warning("Check bin edges format!")

        # (Опционально) показываем предпросмотр
        if bin_labels:
            st.sidebar.write("Bins:", bin_labels)

    return bins_col, bin_labels
