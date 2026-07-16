from collections.abc import Iterable

import pandas as pd
import streamlit as st

from data.loaders import DashboardData
from services.analytics import dataset_as_of_date


def render_page_header(kicker: str, title: str, question: str) -> None:
    st.markdown(f'<div class="ssdc-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(question)


def render_source_banner(data: DashboardData) -> None:
    as_of = dataset_as_of_date(data)
    record_count = sum(len(frame) for frame in data.tables.values())
    as_of_label = as_of.date().isoformat() if not pd.isna(as_of) else "Unavailable"
    if data.is_mock:
        st.markdown(
            f"<div class=\"ssdc-source ssdc-warning\"><strong>Prototype preview:</strong> "
            f"Local cleaned tables were not found, so this page is using anonymized deterministic data. "
            f"Records: {record_count:,} | As-of date: {as_of_label}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class=\"ssdc-source\"><strong>Local cleaned data:</strong> {data.source}. "
            f"Records: {record_count:,} | As-of date: {as_of_label}.</div>",
            unsafe_allow_html=True,
        )
    if data.warnings:
        with st.expander("Data contract notes", expanded=False):
            for warning in data.warnings:
                st.write(f"- {warning}")


def render_kpis(items: Iterable[dict[str, str]], columns_per_row: int | None = None) -> None:
    items = list(items)
    per_row = columns_per_row or len(items)
    for start in range(0, len(items), per_row):
        columns = st.columns(min(per_row, len(items) - start))
        for column, item in zip(columns, items[start : start + per_row]):
            with column:
                st.metric(item["label"], item["value"], help=item.get("help"))


def render_section(title: str, note: str | None = None) -> None:
    st.markdown(f'<div class="ssdc-section"><h3>{title}</h3></div>', unsafe_allow_html=True)
    if note:
        st.caption(note)


def format_count(value: float | int) -> str:
    return f"{int(round(value)):,}"


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def format_days(value: float) -> str:
    return f"{value:.0f} days"
