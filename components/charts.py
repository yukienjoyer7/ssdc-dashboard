from contextlib import contextmanager
from collections.abc import Iterator, Mapping
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from components.carbon_ui import render_feedback
from config.theme import (
    CHART_CATEGORICAL,
    FONT_FAMILY,
    PLOTLY_FONT_SIZES,
    TEXT_COLORS,
    spacing_px,
)


def _base_layout(figure, height: int = 300):
    figure.update_layout(
        height=height,
        margin={
            "l": spacing_px("03"),
            "r": spacing_px("03"),
            "t": spacing_px("09"),
            "b": spacing_px("03"),
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            "family": FONT_FAMILY,
            "size": PLOTLY_FONT_SIZES["body"],
            "color": TEXT_COLORS["primary"],
        },
        colorway=CHART_CATEGORICAL,
        xaxis={
            "gridcolor": "#e0e0e0",
            "linecolor": "#8d8d8d",
            "zerolinecolor": "#8d8d8d",
            "tickfont": {
                "family": FONT_FAMILY,
                "size": PLOTLY_FONT_SIZES["axis"],
                "color": TEXT_COLORS["secondary"],
            },
        },
        yaxis={
            "gridcolor": "#e0e0e0",
            "linecolor": "#8d8d8d",
            "zerolinecolor": "#8d8d8d",
            "tickfont": {
                "family": FONT_FAMILY,
                "size": PLOTLY_FONT_SIZES["axis"],
                "color": TEXT_COLORS["secondary"],
            },
        },
        legend={
            "orientation": "h",
            "y": 1.08,
            "yanchor": "bottom",
            "x": 0,
            "xanchor": "left",
            "font": {
                "family": FONT_FAMILY,
                "size": PLOTLY_FONT_SIZES["legend"],
                "color": TEXT_COLORS["secondary"],
            },
            "title": {"text": ""},
        },
        hoverlabel={
            "font": {
                "family": FONT_FAMILY,
                "size": PLOTLY_FONT_SIZES["tooltip"],
            },
        },
    )
    return figure


def _update_axes(
    figure,
    *,
    x_title: str | None = None,
    y_title: str | None = None,
    tick_angle: int | None = None,
    category_order: list[str] | None = None,
    horizontal: bool = False,
) -> None:
    figure.update_layout(
        xaxis_title=x_title or "",
        yaxis_title=y_title or "",
    )
    if tick_angle is not None:
        figure.update_xaxes(tickangle=tick_angle)
    if category_order:
        axis = "yaxis" if horizontal else "xaxis"
        figure.update_layout(**{axis: {"categoryorder": "array", "categoryarray": category_order}})
    if horizontal:
        figure.update_yaxes(autorange="reversed")


def _chart_title(title: str) -> None:
    st.markdown(f'<div class="carbon-chart-title">{title}</div>', unsafe_allow_html=True)


def _chart_empty(title: str) -> None:
    render_feedback(
        "No chart data",
        "No records match the active filters for this view.",
        key=f"chart-empty-{title.lower().replace(' ', '-')}",
    )


@contextmanager
def chart_surface(
    title: str,
    description: str | None = None,
    *,
    key: str,
    compact: bool = False,
) -> Iterator[None]:
    surface_key = f"cds-chart-surface-{'compact-' if compact else ''}{key}"
    with st.container(
        border=True,
        key=surface_key,
        height="stretch",
        gap=None,
    ):
        description_html = (
            f'<p class="cds-chart-surface__description">{escape(description)}</p>'
            if description
            else ""
        )
        st.markdown(
            '<div class="cds-chart-surface__header">'
            f'<h4 class="cds-chart-surface__title">{escape(title)}</h4>'
            f"{description_html}"
            "</div>",
            unsafe_allow_html=True,
        )
        yield


def render_bar(
    frame: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    height: int = 300,
    *,
    show_title: bool = True,
    color_map: Mapping[str, str] | None = None,
    series_color: str | None = None,
    x_title: str | None = None,
    y_title: str | None = None,
    category_order: list[str] | None = None,
    show_legend: bool | None = None,
    tick_angle: int | None = None,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.bar(
        frame,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=CHART_CATEGORICAL,
        color_discrete_map=dict(color_map or {}),
        text_auto=True,
    )
    if series_color:
        figure.update_traces(marker_color=series_color)
    _update_axes(
        figure,
        x_title=x_title,
        y_title=y_title,
        tick_angle=tick_angle,
        category_order=category_order,
    )
    if show_legend is not None:
        figure.update_layout(showlegend=show_legend)
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_horizontal_bar(
    frame: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    height: int = 320,
    *,
    show_title: bool = True,
    color_map: Mapping[str, str] | None = None,
    series_color: str | None = None,
    x_title: str | None = None,
    y_title: str | None = None,
    category_order: list[str] | None = None,
    show_legend: bool | None = None,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.bar(
        frame,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=CHART_CATEGORICAL,
        color_discrete_map=dict(color_map or {}),
        orientation="h",
        text_auto=True,
    )
    if series_color:
        figure.update_traces(marker_color=series_color)
    _update_axes(
        figure,
        x_title=x_title,
        y_title=y_title,
        category_order=category_order,
        horizontal=True,
    )
    if show_legend is not None:
        figure.update_layout(showlegend=show_legend)
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_line(
    frame: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    height: int = 300,
    *,
    show_title: bool = True,
    color_map: Mapping[str, str] | None = None,
    series_color: str | None = None,
    x_title: str | None = None,
    y_title: str | None = None,
    category_order: list[str] | None = None,
    show_legend: bool | None = None,
    x_type: str | None = None,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.line(
        frame,
        x=x,
        y=y,
        color=color,
        markers=True,
        color_discrete_sequence=CHART_CATEGORICAL,
        color_discrete_map=dict(color_map or {}),
    )
    if series_color:
        figure.update_traces(line_color=series_color, marker_color=series_color)
    _update_axes(
        figure,
        x_title=x_title,
        y_title=y_title,
        category_order=category_order,
    )
    if x_type:
        figure.update_xaxes(type=x_type)
    if show_legend is not None:
        figure.update_layout(showlegend=show_legend)
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_histogram(
    frame: pd.DataFrame,
    x: str,
    title: str,
    color: str | None = None,
    height: int = 300,
    *,
    show_title: bool = True,
    color_map: Mapping[str, str] | None = None,
    series_color: str | None = None,
    x_title: str | None = None,
    y_title: str = "Records",
    show_legend: bool | None = None,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.histogram(
        frame,
        x=x,
        color=color,
        nbins=12,
        color_discrete_sequence=CHART_CATEGORICAL,
        color_discrete_map=dict(color_map or {}),
    )
    if series_color:
        figure.update_traces(marker_color=series_color)
    _update_axes(figure, x_title=x_title, y_title=y_title)
    if show_legend is not None:
        figure.update_layout(showlegend=show_legend)
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_dot_plot(
    frame: pd.DataFrame,
    x: str,
    title: str,
    *,
    x_title: str | None = None,
    height: int = 220,
    show_title: bool = True,
) -> None:
    """Show individual observations without implying a large distribution."""
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    plot_frame = frame[[x]].copy()
    plot_frame["row"] = 0
    figure = px.scatter(plot_frame, x=x, y="row", text=x)
    figure.update_traces(
        marker={"color": "#0f62fe", "size": 11},
        textposition="top center",
        hovertemplate=f"{x_title or x}: %{{x}}<extra></extra>",
    )
    figure.update_yaxes(visible=False, range=[-1, 1])
    _update_axes(figure, x_title=x_title, y_title="")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_insight(value: str, label: str, detail: str | None = None) -> None:
    """Use a compact statement when a chart would have only one meaningful mark."""
    detail_html = f'<p class="cds-chart-insight__detail">{escape(detail)}</p>' if detail else ""
    st.markdown(
        '<div class="cds-chart-insight">'
        f'<div class="cds-chart-insight__value">{escape(value)}</div>'
        f'<p class="cds-chart-insight__label">{escape(label)}</p>'
        f"{detail_html}"
        "</div>",
        unsafe_allow_html=True,
    )
