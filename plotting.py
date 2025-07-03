import plotly.express as px
import streamlit as st

def plot_demo_table(
    df, x_axis, y_axis,
    color_map_user, symbol_map_user, size_map_user,
    log_x=False, log_y=False,
    styles=None, bg_color="#ffffff", font_color="#000000"
):
    plot_df = df.copy()
    size_col = "__marker_size"
    if "type" in plot_df.columns:
        plot_df[size_col] = plot_df["type"].map(size_map_user).fillna(20)
    else:
        plot_df[size_col] = 20

    plot_args = dict(
        x=x_axis,
        y=y_axis,
        data_frame=plot_df,
        log_x=log_x,
        log_y=log_y,
        height=650
    )
    if "type_loc" in plot_df.columns:
        plot_args["color"] = plot_df["type_loc"].astype(str)
        plot_args["color_discrete_map"] = color_map_user
    if "type" in plot_df.columns:
        plot_args["symbol"] = plot_df["type"].astype(str)
        plot_args["symbol_map"] = symbol_map_user
    if size_col in plot_df.columns:
        plot_args["size"] = plot_df[size_col]
    if "type_loc" in plot_df.columns:
        plot_args["hover_name"] = "type_loc"

    fig = px.scatter(**plot_args)
    if styles:
        for tr in fig.data:
            st_dict = styles.get(tr.name, {})
            tr.marker.line.color = st_dict.get("outline_color", "#000")
            tr.marker.line.width = st_dict.get("outline_width", 1.0)
            tr.marker.opacity    = st_dict.get("opacity", 0.9)
    fig.update_traces(marker=dict(sizemode="diameter", sizeref=2.0, sizemin=2))
    fig.update_layout(
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
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    return fig


def plot_user_table(
    df, x_axis, y_axis, group_col,
    color_map_user=None, symbol_map_user=None,
    size_map_user=None, opacity_map_user=None,
    log_x=False, log_y=False,
    styles=None, bg_color="#ffffff", font_color="#000000"
):
    plot_df = df.copy()

    # ВАЖНО: Сначала приводи к строке!
    if group_col and group_col in plot_df.columns:
        plot_df[group_col] = plot_df[group_col].astype(str)
        color_series = plot_df[group_col]
        symbol_series = plot_df[group_col]
        # Индивидуальный размер для каждой группы
        if size_map_user:
            plot_df["__marker_size"] = plot_df[group_col].map(size_map_user).fillna(20)
        else:
            plot_df["__marker_size"] = 20
        # Индивидуальная прозрачность для каждой группы
        if opacity_map_user:
            plot_df["__marker_opacity"] = plot_df[group_col].map(opacity_map_user).fillna(0.9)
        else:
            plot_df["__marker_opacity"] = 0.9
    else:
        color_series = None
        symbol_series = None
        plot_df["__marker_size"] = 20
        plot_df["__marker_opacity"] = 0.9

    plot_args = dict(
        x=x_axis,
        y=y_axis,
        data_frame=plot_df,
        log_x=log_x,
        log_y=log_y,
        height=650,
        size=plot_df["__marker_size"],
        size_max=80,  # увеличь max если надо
    )

    if group_col and group_col in plot_df.columns:
        plot_args["color"] = color_series
        if color_map_user:
            plot_args["color_discrete_map"] = color_map_user
        # Символы работают только для ограниченного числа групп (<15)
        if plot_df[group_col].nunique() < 15:
            plot_args["symbol"] = symbol_series
            if symbol_map_user:
                plot_args["symbol_map"] = symbol_map_user
        plot_args["hover_name"] = group_col

    st.write("size_map_user:", size_map_user)
    st.write("plot_df[[group_col, '__marker_size']].head(10):", plot_df[[group_col, "__marker_size"]].head(10))
    st.write("color_series nunique:", color_series.nunique())
    st.write("group counts:", plot_df[group_col].value_counts())

    fig = px.scatter(**plot_args)

    # Установка индивидуальной прозрачности
    if opacity_map_user and group_col and group_col in plot_df.columns:
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
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    return fig

