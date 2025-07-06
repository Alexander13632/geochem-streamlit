import streamlit as st
import pandas as pd

def filter_dataframe(df):
    """UI for online data filtering. Returns the filtered DataFrame."""
    if "filters" not in st.session_state:
        st.session_state.filters = []

    st.sidebar.header("Data Filters")
    add_filter = st.sidebar.button("➕  Add filter", key="add_filter")

    # Добавить фильтр по клику
    if add_filter:
        st.session_state.filters.append({"col": df.columns[0], "op": ">", "val": 0.0})

    # ── Шапка таблицы (один раз) ──────────────────────────────────────
    hdr = st.sidebar.columns([3, 2, 3, 0.8])
    hdr[0].markdown("**Column**")
    hdr[1].markdown("**Operator**")
    hdr[2].markdown("**Value**")
    hdr[3].markdown("")  # место под крестик

    # ── Строки фильтров ───────────────────────────────────────────────
    for i, f in enumerate(st.session_state.filters):
        cols = st.sidebar.columns([3, 2, 3, 0.8])

        col = cols[0].selectbox(
            "", df.columns,
            index=list(df.columns).index(f["col"]),
            key=f"f_col_{i}", label_visibility="collapsed"
        )
        op  = cols[1].selectbox(
            "", [">", "<", ">=", "<=", "==", "!="],
            index=[">", "<", ">=", "<=", "==", "!="].index(f["op"]),
            key=f"f_op_{i}", label_visibility="collapsed"
        )
        val = cols[2].text_input(
            "", value=str(f["val"]),
            key=f"f_val_{i}", label_visibility="collapsed"
        )

        remove = cols[3].button("✖", key=f"f_rm_{i}", use_container_width=True)

        st.session_state.filters[i] = {"col": col, "op": op, "val": val}
        if remove:
            st.session_state.filters.pop(i)
            st.rerun()

    # Фильтрация данных
    filtered_df = df.copy()
    for f in st.session_state.filters:
        col = f["col"]
        op = f["op"]
        val = f["val"]
        # Попробовать преобразовать val к float, если колонка числовая
        if pd.api.types.is_numeric_dtype(df[col]):
            try:
                val_cast = float(val)
            except:
                continue
        else:
            val_cast = val
        # Применить фильтр
        if op == ">":
            filtered_df = filtered_df[filtered_df[col] > val_cast]
        elif op == "<":
            filtered_df = filtered_df[filtered_df[col] < val_cast]
        elif op == ">=":
            filtered_df = filtered_df[filtered_df[col] >= val_cast]
        elif op == "<=":
            filtered_df = filtered_df[filtered_df[col] <= val_cast]
        elif op == "==":
            filtered_df = filtered_df[filtered_df[col] == val_cast]
        elif op == "!=":
            filtered_df = filtered_df[filtered_df[col] != val_cast]
    return filtered_df