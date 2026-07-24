import streamlit as st

from data.contracts import FilterState
from data.loaders import DashboardData, load_dashboard_data
from components.ui import render_data_status


def get_context() -> tuple[DashboardData, FilterState]:
    data = load_dashboard_data()
    filters = st.session_state.get("global_filters", FilterState())
    return data, filters


def start_page(
    kicker: str,
    title: str,
    question: str,
    *,
    provisional_note: str,
) -> tuple[DashboardData, FilterState]:
    data, filters = get_context()
    from components.ui import render_page_header

    render_page_header(kicker, title, question)
    render_data_status(
        data,
        provisional_note,
        key=f"data-status-{title.lower().replace(' ', '-')}",
    )
    return data, filters
