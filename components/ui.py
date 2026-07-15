from collections.abc import Iterable

import streamlit as st

from data.loaders import DashboardData


def render_page_header(kicker: str, title: str, question: str) -> None:
    st.markdown(f'<div class="ssdc-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(question)


def render_source_banner(data: DashboardData) -> None:
    if data.is_mock:
        st.markdown(
            "<div class=\"ssdc-source ssdc-warning\"><strong>Prototype preview:</strong> "
            "Local cleaned tables were not found, so this page is using anonymized deterministic data.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class=\"ssdc-source\"><strong>Local cleaned data:</strong> {data.source}. "
            "Prototype-derived metrics remain pending validation.</div>",
            unsafe_allow_html=True,
        )
    if data.warnings:
        with st.expander("Data contract notes", expanded=False):
            for warning in data.warnings:
                st.write(f"- {warning}")


def render_kpis(items: Iterable[dict[str, str]]) -> None:
    items = list(items)
    columns = st.columns(len(items))
    for column, item in zip(columns, items):
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
