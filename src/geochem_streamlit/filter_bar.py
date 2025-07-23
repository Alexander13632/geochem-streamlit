import streamlit as st
import pandas as pd


def filter_dataframe(df, plot_type=None):
    key_suffix = f"_{plot_type}" if plot_type else ""
    """UI for online data filtering. Returns the filtered DataFrame."""
    if "filters" not in st.session_state:
        st.session_state.filters = []

    # Добавляем состояние для логики фильтрации
    if f"filter_logic{key_suffix}" not in st.session_state:
        st.session_state[f"filter_logic{key_suffix}"] = "AND"

    st.sidebar.header("Data Filters")

    # Выбор логики фильтрации
    filter_logic = st.sidebar.radio(
        "Filter Logic:",
        ["AND", "OR"],
        index=0 if st.session_state[f"filter_logic{key_suffix}"] == "AND" else 1,
        key=f"filter_logic_radio{key_suffix}",
        horizontal=True,
    )
    st.session_state[f"filter_logic{key_suffix}"] = filter_logic

    add_filter = st.sidebar.button("➕  Add filter", key=f"add_filter{key_suffix}")

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
            "",
            df.columns,
            index=list(df.columns).index(f["col"]),
            key=f"f_col_{i}{key_suffix}",
            label_visibility="collapsed",
        )
        op = cols[1].selectbox(
            "",
            [">", "<", ">=", "<=", "==", "!="],
            index=[">", "<", ">=", "<=", "==", "!="].index(f["op"]),
            key=f"f_op_{i}{key_suffix}",
            label_visibility="collapsed",
        )
        val = cols[2].text_input(
            "",
            value=str(f["val"]),
            key=f"f_val_{i}{key_suffix}",
            label_visibility="collapsed",
        )

        remove = cols[3].button(
            "✖", key=f"f_rm_{i}{key_suffix}", use_container_width=True
        )

        st.session_state.filters[i] = {"col": col, "op": op, "val": val}
        if remove:
            st.session_state.filters.pop(i)
            st.rerun()

    # Фильтрация данных
    if not st.session_state.filters:
        return df.copy()

    # Создаем маски для каждого фильтра
    masks = []
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

        # Создать маску для текущего фильтра
        if op == ">":
            mask = df[col] > val_cast
        elif op == "<":
            mask = df[col] < val_cast
        elif op == ">=":
            mask = df[col] >= val_cast
        elif op == "<=":
            mask = df[col] <= val_cast
        elif op == "==":
            mask = df[col] == val_cast
        elif op == "!=":
            mask = df[col] != val_cast
        else:
            continue

        masks.append(mask)

    # Объединяем маски в зависимости от выбранной логики
    if masks:
        if filter_logic == "AND":
            # Логика И - все условия должны быть истинными
            final_mask = masks[0]
            for mask in masks[1:]:
                final_mask = final_mask & mask
        else:
            # Логика ИЛИ - хотя бы одно условие должно быть истинным
            final_mask = masks[0]
            for mask in masks[1:]:
                final_mask = final_mask | mask

        return df[final_mask].copy()
    else:
        return df.copy()
