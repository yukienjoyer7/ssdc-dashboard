from collections.abc import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st


COLORS = ["#087f8c", "#b56b00", "#b42318", "#18794e", "#61707d"]


def _base_layout(figure, height: int = 330):
    title_text = figure.layout.title.text if figure.layout.title else None
    figure.update_layout(
        height=height,
        margin={"l": 10, "r": 10, "t": 82, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": "#17212b"},
        title={"text": title_text, "x": 0, "xanchor": "left", "y": 1.0, "yanchor": "bottom"},
        legend={"orientation": "h", "y": 1.24, "yanchor": "bottom", "x": 0, "xanchor": "left"},
    )
    return figure


def render_bar(frame: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 330) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    figure = px.bar(frame, x=x, y=y, color=color, color_discrete_sequence=COLORS, text_auto=True)
    figure.update_layout(title=title, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_horizontal_bar(frame: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 360) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    figure = px.bar(frame, x=x, y=y, color=color, color_discrete_sequence=COLORS, orientation="h", text_auto=True)
    figure.update_layout(title=title, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_line(frame: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, height: int = 330) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    figure = px.line(frame, x=x, y=y, color=color, markers=True, color_discrete_sequence=COLORS)
    figure.update_layout(title=title, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})


def render_histogram(frame: pd.DataFrame, x: str, title: str, color: str | None = None, height: int = 330) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    figure = px.histogram(frame, x=x, color=color, nbins=12, color_discrete_sequence=COLORS)
    figure.update_layout(title=title, xaxis_title=None, yaxis_title="Records")
    st.plotly_chart(_base_layout(figure, height), width="stretch", config={"displayModeBar": False})
