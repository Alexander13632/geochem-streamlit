import plotly.graph_objects as go
import streamlit as st
import pandas as pd

AXIS_STYLE = dict(
    linecolor="#000000", mirror=True, showline=True,
    ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
    gridcolor="rgba(0,0,0,0.15)",
    minor_showgrid=True, minor_gridwidth=0.5,
    minor_gridcolor="rgba(0,0,0,0.05)",
    title_font=dict(size=18, color="#111111"),
    tickfont=dict(size=14, color="#111111"),
)

FIELD_LABELS = {
    "Picro-basalt":        (42.5,  2),
    "Basalt":              (47,  4.0),
    "Basaltic andesite":   (49,  6.2),
    "Andesite":            (53,  8.3),
    "Dacite":              (57,  8.0),
    "Rhyolite":            (72,  8.0),
    "Basanite":            (43,  7.0),
    "Phonotephrite":        (48, 9.0),
    "Tephriphonolite":      (53, 12.0),
    "Phonolite":          (57.5, 13.0),
    "Trachyte":           (65, 11.0),
    "Basaltic andesite": (54, 4.0),
    "Andesite":        (60, 4.0),
    "Dacite":          (68, 4.0),
    "Trachybasalt": (49, 6.0),
    "Basaltic trachy-andesite": (53, 7.0),
    "Trachy-andesite": (58, 9.0)

    # … добавьте остальные …
}

def add_field_labels(fig, labels=FIELD_LABELS,
                     font_size=12, font_color="#000000", opacity=0.9):
    """Кладёт подписи TAS-полей по фиксированным координатам."""
    for name, (x, y) in labels.items():
        fig.add_annotation(
            x=x, y=y, text=name,
            showarrow=False,
            font=dict(size=font_size, color=font_color),
            opacity=opacity,
            align="center",
            hovertext=name,
        )



def empty_tas_figure():
    fig = go.Figure()

    # ── оси и диапазоны ─────────────────────────────────────────
    fig.update_layout(
        xaxis=dict(title="SiO₂ (wt %)", range=[35, 80], **AXIS_STYLE),
        yaxis=dict(title="Na₂O + K₂O (wt %)", range=[0, 15], **AXIS_STYLE),
        height=800, width=700,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        showlegend=True
    )

    # ── координаты «сегментов» (ваш список ax1.plot) ────────────
    segments = [
        ([41, 41], [0.5, 3.0]),
        ([41, 41], [3.0, 7.0]),
        ([45, 45], [0.5, 3.0]),
        ([41, 45], [3.0, 3.0]),
        ([45, 45], [3.0, 5.0]),
        ([52, 52], [0.5, 5.0]),
        ([45, 52], [5.0, 5.0]),
        ([45, 49.4], [5.0, 7.3]),
        ([49.4, 52], [7.3, 5.0]),
        ([52, 57], [5.0, 5.9]),
        ([49.4, 53], [7.3, 9.3]),
        ([41, 45], [7.0, 9.4]),
        ([45, 49.4], [9.4, 7.3]),
        ([57, 63], [5.9, 7.0]),
        ([57, 57], [0.5, 5.9]),
        ([57, 53], [5.9, 9.3]),
        ([45, 48.4], [9.4, 11.5]),
        ([48.4, 53], [11.5, 9.3]),
        ([48.4, 52.5], [11.5, 14.0]),
        ([52.5, 57.6], [14.0, 11.7]),
        ([53, 57.6], [9.3, 11.7]),
        ([57.6, 63], [11.7, 7.0]),
        ([63, 63], [7.0, 0.5]),
        ([63, 69], [7.0, 8.0]),
        ([69, 69], [8.0, 14.0]),
        ([69, 77.5], [8.0, 0.5]),
        ([57.6, 61], [11.7, 13.5]),
    ]
    for x, y in segments:
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(color="black", width=0.5),
            hoverinfo="skip", showlegend=False)
        )


    add_field_labels(fig)
    return fig


def plot_tas_diagram(
    df, x_col, y_col, group_col=None,
    color_map_user=None, symbol_map_user=None,
    size_map_user=None, styles=None,
    base_fig=None, hover_cols=None
):
    hover_cols = hover_cols or []
    # отфильтруем только существующие в df колонки
    hover_cols = [c for c in hover_cols if c in df.columns]

    # 1) если base_fig задан → берём его, иначе создаём de-novo
    fig = base_fig if base_fig is not None else empty_tas_figure()

    # 2) далее только добавляем точки
    if group_col and group_col in df.columns:
        for group, sdf in df.groupby(group_col):
            marker = dict(
                size   = size_map_user.get(group, 10) if size_map_user else 10,
                color  = color_map_user.get(group, "#1f77b4") if color_map_user else "#1f77b4",
                symbol = symbol_map_user.get(group, "circle") if symbol_map_user else "circle",
            )
            if styles and group in styles:
                stl = styles[group]
                marker.update(
                    line=dict(color=stl.get("outline_color", "#000"),
                              width=stl.get("outline_width", 1.0)),
                    opacity=stl.get("opacity", 0.9),
                )
            fig.add_trace(go.Scatter(
                x=sdf[x_col], y=sdf[y_col],
                mode="markers", name=str(group), showlegend=True, marker=marker))
    else:
        fig.add_trace(go.Scatter(
            x=df[x_col], y=df[y_col],
            mode="markers", showlegend=True, marker=dict(size=10, color="red"), name="Samples"))
    fig.update_layout(
        showlegend=True,
        legend=dict(
            title=group_col or "Group",
            font=dict(size=12, color="#000000"),
            bordercolor="#aaa", borderwidth=0.5,
        ),
        font=dict(color="#000000")
)
    return fig



def show_tas(
    df, user_data,
    base_color, base_symbol, base_size,
    build_group_style, group_style_editor,
    filter_dataframe, hover_cols=None
):
    """
    Отрисовывает виджеты TAS, строит график, делает st.stop().
    Вызывается из app.py вместо большого if-блока.
    """
    # 1. выбор колонок
    si_col = st.sidebar.selectbox("SiO₂ column", [""] + list(df.columns), index=0)
    na_col = st.sidebar.selectbox("Na₂O column", [""] + list(df.columns), index=0)
    k_col  = st.sidebar.selectbox("K₂O column",  [""] + list(df.columns), index=0)

    if not si_col or not na_col or not k_col:
        st.info("Choose SiO₂, Na₂O and K₂O columns to plot your data")
        st.plotly_chart(empty_tas_figure(), use_container_width=True)
        st.stop()

    # 2. группировка
    default_group = "type" if (not user_data and "type" in df.columns) else ""
    group_opts    = [""] + list(df.columns)
    group_col = st.sidebar.selectbox(
        "Grouping variable (color)",
        group_opts,
        index=group_opts.index(default_group) if default_group else 0,
    )
    group_for_plot = group_col or None

    # 3. карты стилей
    if group_for_plot:
        color_map_user, symbol_map_user, size_map_user = build_group_style(
            df, group_for_plot, base_color, base_symbol, base_size
        )
        opacity_map_user = {g: 0.9 for g in color_map_user}

        st.sidebar.markdown(f"---\n### Color & Trace style ({group_for_plot})")
        color_map_user, symbol_map_user, size_map_user, opacity_map_user = group_style_editor(
            list(color_map_user.keys()),
            color_map_user, symbol_map_user,
            size_map_user, opacity_map_user
        )
    else:
        color_map_user = base_color.copy()
        symbol_map_user = base_symbol.copy()
        size_map_user   = base_size.copy()
        opacity_map_user = {g: 0.9 for g in color_map_user}

    styles = {
        g: {
            "color"  : color_map_user[g],
            "symbol" : symbol_map_user[g],
            "size"   : size_map_user[g],
            "opacity": opacity_map_user[g],
        }
        for g in color_map_user
    }

    # 4. подготовка данных
    df = df.copy()
    df["Na2O+K2O"] = (
        pd.to_numeric(df[na_col], errors="coerce") +
        pd.to_numeric(df[k_col],  errors="coerce")
    )
    df = filter_dataframe(df, "TAS diagram")

    # 5. график
    base = empty_tas_figure()
    fig = plot_tas_diagram(
        df,
        x_col=si_col, y_col="Na2O+K2O",
        group_col=group_for_plot,
        color_map_user=color_map_user,
        symbol_map_user=symbol_map_user,
        size_map_user=size_map_user,
        styles=styles
    )
    st.plotly_chart(fig, use_container_width=True, key="tas_diagram_chart")
    
    # ВМЕСТО st.stop() возвращаем fig и plot_df для экспорта
    return fig, df  # Возвращаем для экспорта

