import pandas as pd
import streamlit as st

def binning_widget(df: pd.DataFrame, group_col: str):
    if not group_col or not pd.api.types.is_numeric_dtype(df[group_col]):
        return None, None

    k = group_col
    st.sidebar.markdown(f"### Binning for **{group_col}**")

    mode = st.sidebar.radio("Binning mode",
                            ["Equal width", "Manual"],
                            horizontal=True, key=f"bin_mode_{k}")

    series = pd.to_numeric(df[group_col], errors="coerce")   # безопасно

    def _rename_and_save(cut, labels):
        bin_col = f"{group_col}_bin"
        # заменяем только категории, пропуски остаются NaN
        df[bin_col] = cut.cat.rename_categories(labels)
        return bin_col


    if mode == "Equal width":
        n_bins = st.sidebar.slider("Number of bins", 2, 15, 4,
                                   key=f"bin_nbins_{k}")
        cut, edges = pd.cut(series, bins=n_bins,
                            include_lowest=True, retbins=True)
        labels = [f"{round(l,2)}–{round(r,2)}"
                  for l, r in zip(edges[:-1], edges[1:])]
        bin_col = _rename_and_save(cut, labels)

    else:  # Manual
        mn, mx = float(series.min()), float(series.max())
        raw = st.sidebar.text_input("Enter bin edges (comma-separated)",
                                    value=f"{mn:.2f},{mx:.2f}",
                                    key=f"bin_edges_{k}")
        try:
            edges = [float(x.strip()) for x in raw.split(",") if x.strip()]
            if len(edges) < 2:
                raise ValueError
            cut = pd.cut(series, bins=edges, include_lowest=True)
            labels = [f"{edges[i]}–{edges[i+1]}"
                      for i in range(len(edges)-1)]
            bin_col = _rename_and_save(cut, labels)
        except ValueError:
            st.sidebar.warning("Введите минимум две числовых точки через запятую")
            return None, None

    st.sidebar.write("Bins:", labels)
    return bin_col, labels


