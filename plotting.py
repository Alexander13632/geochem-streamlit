import plotly.express as px
import streamlit as st

def plot_demo_table(
    df, x_axis, y_axis,
    group_for_plot,                 # ← новый аргумент
    color_map_user, symbol_map_user, size_map_user,
    log_x=False, log_y=False,
    hover_cols=None,
    styles=None,
    bg_color="#ffffff", font_color="#000000"
):
    # 1) копия исходного DataFrame
    plot_df = df.copy()

    # 2) определяем колонку группировки
    grp = group_for_plot or "type_loc"
    if grp not in plot_df.columns:
        raise ValueError(f"Column '{grp}' not found in DataFrame")

    # 3) выбрасываем строки без группового значения
    plot_df = plot_df[plot_df[grp].notna()].copy()

    # ---------- далее идёт остальной код, который уже был ----------
    size_col = "__marker_size"
    plot_df[size_col] = plot_df[grp].map(size_map_user).fillna(5)


    hover_dict = {c: True for c in hover_cols}
    hover_dict[size_col] = False


    plot_args = dict(
        x=x_axis,
        y=y_axis,
        data_frame=plot_df,
        log_x=log_x,
        log_y=log_y,
        height=650,
        color              = plot_df[grp].astype(str),
        color_discrete_map = color_map_user,
        symbol             = plot_df[grp].astype(str),
        symbol_map         = symbol_map_user,
        size               = plot_df[size_col],
        hover_name         = grp,
        hover_data = hover_dict,
    )

    fig = px.scatter(**plot_args)          # без size_max !
    fig.update_traces(
    marker=dict(sizemode="diameter", sizeref=1, sizemin=7)
)

    #------------------------------------------------------------------
    # 4) Применяем outline, opacity и пр.
    #------------------------------------------------------------------
    if styles:
        for tr in fig.data:
            st_dict = styles.get(tr.name, {})
            tr.marker.line.color = st_dict.get("outline_color", "#000")
            tr.marker.line.width = st_dict.get("outline_width", 1.0)
            tr.marker.opacity    = st_dict.get("opacity", 0.9)
    
    fig.update_layout(
        xaxis_title=x_axis,
        yaxis_title=y_axis,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        legend=dict(font=dict(color=font_color)),
        font=dict(color=font_color),
    )

    axis_style = dict(
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
    )

    fig.update_xaxes(
        title_text=x_axis,
        title_font=dict(size=18, color="#111111"),
        tickfont=dict(size=14, color="#111111"),    # <--- ВАЖНО!
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
    )
    fig.update_yaxes(
        title_text=y_axis,
        title_font=dict(size=18, color="#111111"),
        tickfont=dict(size=14, color="#111111"),    # <--- ВАЖНО!
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
)

    return fig


def plot_user_table(
    df, x_axis, y_axis, group_for_plot,
    color_map_user=None, symbol_map_user=None,
    size_map_user=None, opacity_map_user=None,
    log_x=False, log_y=False,
    styles=None, bg_color="#ffffff", font_color="#000000",
    hover_cols=None
):
    plot_df = df.copy()

    # ВАЖНО: Сначала приводи к строке!
    if group_for_plot and group_for_plot in plot_df.columns:
        plot_df[group_for_plot] = plot_df[group_for_plot].astype(str)
        color_series = plot_df[group_for_plot]
        symbol_series = plot_df[group_for_plot]
        # Индивидуальный размер для каждой группы
        if size_map_user:
            plot_df["__marker_size"] = plot_df[group_for_plot].map(size_map_user).fillna(20)
        else:
            plot_df["__marker_size"] = 20
        # Индивидуальная прозрачность для каждой группы
        if opacity_map_user:
            plot_df["__marker_opacity"] = plot_df[group_for_plot].map(opacity_map_user).fillna(0.9)
        else:
            plot_df["__marker_opacity"] = 0.9
    else:
        color_series = None
        symbol_series = None
        plot_df["__marker_size"] = 15
        plot_df["__marker_opacity"] = 0.9

    hover_dict = {c: True for c in hover_cols}
    hover_dict["__marker_size"] = False

    plot_args = dict(
        x=x_axis,
        y=y_axis,
        data_frame=plot_df,
        log_x=log_x,
        log_y=log_y,
        height=650,
        size=plot_df["__marker_size"],
        hover_data=hover_dict,
        size_max=80,  # увеличь max если надо
    )

    if group_for_plot and group_for_plot in plot_df.columns:
        plot_args["color"] = color_series
        if color_map_user:
            plot_args["color_discrete_map"] = color_map_user
        # Символы работают только для ограниченного числа групп (<15)
        if plot_df[group_for_plot].nunique() < 30:
            plot_args["symbol"] = symbol_series
            if symbol_map_user:
                plot_args["symbol_map"] = symbol_map_user
        plot_args["hover_name"] = group_for_plot


    fig = px.scatter(**plot_args)          # без size_max !
    fig.update_traces(
    marker=dict(sizemode="diameter", sizeref=1, sizemin=7)
)

    # Установка индивидуальной прозрачности
    if opacity_map_user and group_for_plot and group_for_plot in plot_df.columns:
        for tr in fig.data:
            group = tr.name
            tr.marker.opacity = opacity_map_user.get(group, 0.9)

    # (Доп. стили — необязательно)
    if styles:
        for tr in fig.data:
            st_dict = styles.get(tr.name, {})
            tr.marker.line.color = st_dict.get("outline_color", "#000")
            tr.marker.line.width = st_dict.get("outline_width", 1.0)
            # Не переопределяй marker.opacity тут!

    fig.update_traces(marker=dict(sizemode="diameter", sizeref=2.0, sizemin=2))
   
    fig.update_layout(
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            legend=dict(font=dict(color=font_color)),
            font=dict(color=font_color),
        )
    

    axis_style = dict(
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
    )
    fig.update_xaxes(
        title_text=x_axis,
        title_font=dict(size=18, color="#111111"),
        tickfont=dict(size=14, color="#111111"),    # <--- ВАЖНО!
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
    )
    fig.update_yaxes(
        title_text=y_axis,
        title_font=dict(size=18, color="#111111"),
        tickfont=dict(size=14, color="#111111"),    # <--- ВАЖНО!
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
    )

    return fig

def plot_box_plot(
        df,
        x: str,
        y: str,
        color: str | None = None,
        color_map: dict | None = None,
        symbol_map: dict | None = None,
        size_map: dict | None = None,
        opacity_map: dict | None = None,
        outline_color_map: dict | None = None,
        outline_width_map: dict | None = None,
        bg_color: str = "#ffffff",
        font_color: str = "#000000",
        hover_cols=None
):

    # --- 1. безопасный список колонок для tooltip ----------------
    hover_cols = hover_cols or []                       # None → []
    hover_dict = {c: True for c in hover_cols if c in df.columns}

    # скрывать служебный столбец только если он реально существует
    if "__marker_size" in df.columns:
        hover_dict["__marker_size"] = False

    fig = px.box(
        df,
        x=x,
        y=y,
        color=color if color else x,
        points="all",
        notched=False,
        height=650,
        color_discrete_map=color_map or {},
        width=None,
        hover_data=hover_dict
    )

    # 2️⃣ Перебор трэйсов и кастомизация точек по группам
    for trace in fig.data:
        group = trace.name
        marker_args = {}
        if symbol_map and group in symbol_map:
            marker_args['symbol'] = symbol_map[group]
        if size_map and group in size_map:
            marker_args['size'] = size_map[group]
        if opacity_map and group in opacity_map:
            marker_args['opacity'] = opacity_map[group]
        if outline_color_map and group in outline_color_map:
            marker_args.setdefault('line', {})['color'] = outline_color_map[group]
        if outline_width_map and group in outline_width_map:
            marker_args.setdefault('line', {})['width'] = outline_width_map[group]
        trace.update(
            marker=marker_args,
            jitter=0.3,
            pointpos=0,
            line=dict(width=1.5),
            whiskerwidth=0.4,
            width=0.4,
        )

    # 3️⃣ оси, сетка, шрифты
    axis_style = dict(
        linecolor="#000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000",
        gridcolor="rgba(0,0,0,0.12)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
        title_font=dict(size=18, color=font_color),
        tickfont=dict(size=14, color=font_color),
    )
    fig.update_xaxes(**axis_style, tickangle=45)
    fig.update_yaxes(**axis_style)

    fig.update_layout(
        boxmode="group",
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        legend=dict(font=dict(size=14, color=font_color)),
        font=dict(color=font_color, size=16),
        xaxis_title=x,
        yaxis_title=y,
        margin=dict(l=80, r=60, t=40, b=100),
    )

    st.plotly_chart(fig, use_container_width=True)
    return fig



