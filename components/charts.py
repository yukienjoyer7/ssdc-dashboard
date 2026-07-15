from collections.abc import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st


COLORS = ["#087f8c", "#b56b00", "#b42318", "#18794e", "#61707d"]


def _base_layout(figure, height: int = 330):
    figure.update_layout(
        height=height,
        margin={"l": 10, "r": 10, "t": 58, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": "#17212b"},
        legend={"orientation": "h", "y": 1.08, "yanchor": "bottom", "x": 0, "xanchor": "left"},
    )
    return figure


def _chart_title(title: str) -> None:
    st.markdown(f'<div class="ssdc-chart-title">{title}</div>', unsafe_allow_html=True)


def render_bar(frame: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 330) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    _chart_title(title)
    figure = px.bar(frame, x=x, y=y, color=color, color_discrete_sequence=COLORS, text_auto=True)
    figure.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_horizontal_bar(frame: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 360) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    _chart_title(title)
    figure = px.bar(frame, x=x, y=y, color=color, color_discrete_sequence=COLORS, orientation="h", text_auto=True)
    figure.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_line(frame: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 330) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    _chart_title(title)
    figure = px.line(frame, x=x, y=y, color=color, markers=True, color_discrete_sequence=COLORS)
    figure.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_histogram(frame: pd.DataFrame, x: str, title: str, color: str | None = None, height: int = 330) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    _chart_title(title)
    figure = px.histogram(frame, x=x, color=color, nbins=12, color_discrete_sequence=COLORS)
    figure.update_layout(xaxis_title="", yaxis_title="Records")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})
