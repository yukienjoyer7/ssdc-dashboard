from collections.abc import Iterable

import pandas as pd
import streamlit as st

from components.carbon_ui import render_feedback, render_kpi_row
from data.loaders import DashboardData
from services.analytics import dataset_as_of_date


def render_page_header(kicker: str, title: str, question: str) -> None:
    st.markdown(f'<div class="carbon-page-header"><span>{kicker}</span></div>', unsafe_allow_html=True)
    st.header(title)
    st.caption(question)


def render_source_banner(data: DashboardData) -> None:
    as_of = dataset_as_of_date(data)
    record_count = sum(len(frame) for frame in data.tables.values())
    as_of_label = as_of.date().isoformat() if not pd.isna(as_of) else "Unavailable"
    if data.is_mock:
        render_feedback(
            "Prototype preview",
            "Local cleaned tables were not found; this page is using anonymized deterministic data. "
            f"Records: {record_count:,} · As-of date: {as_of_label}",
            kind="warning",
            key="source-warning",
        )
    else:
        render_feedback(
            "Local cleaned data",
            f"{data.source} · Records: {record_count:,} · As-of date: {as_of_label}",
            key="source-status",
        )
    if data.warnings:
        with st.expander("Data contract notes", expanded=False):
            for warning in data.warnings:
                st.write(f"- {warning}")


def render_kpis(items: Iterable[dict[str, str]], columns_per_row: int | None = None, key: str | None = None) -> None:
    items = list(items)
    if not items:
        return
    render_kpi_row(
        items,
        key=key or "carbon-kpis-" + "-".join(item["label"].lower().replace(" ", "-") for item in items),
    )


def render_section(title: str, note: str | None = None) -> None:
    st.markdown(f'<div class="carbon-section"><h3>{title}</h3></div>', unsafe_allow_html=True)
    if note:
        st.caption(note)


def format_count(value: float | int) -> str:
    return f"{int(round(value)):,}"


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def format_days(value: float) -> str:
    return f"{value:.0f} days"
