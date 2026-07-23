from contextlib import contextmanager
from collections.abc import Iterable
from collections.abc import Iterator
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

from components.carbon_ui import render_feedback
from config.theme import CARBON_CHART_COLORS

COLORS = CARBON_CHART_COLORS


def _base_layout(figure, height: int = 330):
    figure.update_layout(
        height=height,
        margin={"l": 10, "r": 10, "t": 58, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "'IBM Plex Sans', sans-serif", "color": "#161616"},
        colorway=COLORS,
        xaxis={"gridcolor": "#e0e0e0", "linecolor": "#8d8d8d", "zerolinecolor": "#8d8d8d"},
        yaxis={"gridcolor": "#e0e0e0", "linecolor": "#8d8d8d", "zerolinecolor": "#8d8d8d"},
        legend={"orientation": "h", "y": 1.08, "yanchor": "bottom", "x": 0, "xanchor": "left"},
    )
    return figure


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
) -> Iterator[None]:
    with st.container(
        border=True,
        key=f"cds-chart-surface-{key}",
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
    height: int = 330,
    *,
    show_title: bool = True,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.bar(frame, x=x, y=y, color=color, color_discrete_sequence=COLORS, text_auto=True)
    figure.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_horizontal_bar(
    frame: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    height: int = 360,
    *,
    show_title: bool = True,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.bar(frame, x=x, y=y, color=color, color_discrete_sequence=COLORS, orientation="h", text_auto=True)
    figure.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_line(
    frame: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str | None = None,
    height: int = 330,
    *,
    show_title: bool = True,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.line(frame, x=x, y=y, color=color, markers=True, color_discrete_sequence=COLORS)
    figure.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_histogram(
    frame: pd.DataFrame,
    x: str,
    title: str,
    color: str | None = None,
    height: int = 330,
    *,
    show_title: bool = True,
) -> None:
    if frame.empty:
        _chart_empty(title)
        return
    if show_title:
        _chart_title(title)
    figure = px.histogram(frame, x=x, color=color, nbins=12, color_discrete_sequence=COLORS)
    figure.update_layout(xaxis_title="", yaxis_title="Records")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})
