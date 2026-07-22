import streamlit as st

from data.contracts import FilterState
from data.loaders import DashboardData, load_dashboard_data
from components.ui import render_source_banner


def get_context() -> tuple[DashboardData, FilterState]:
    data = load_dashboard_data()
    filters = st.session_state.get("global_filters", FilterState())
    return data, filters


def start_page(kicker: str, title: str, question: str) -> tuple[DashboardData, FilterState]:
    data, filters = get_context()
    from components.ui import render_page_header

    render_page_header(kicker, title, question)
    render_source_banner(data)
    return data, filters
