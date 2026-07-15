from datetime import date

import streamlit as st

from data.contracts import FilterState
from data.loaders import DashboardData
from services.analytics import (
    company_options,
    date_bounds,
    placement_type_options,
    request_status_options,
    study_program_options,
)


FILTER_KEYS = (
    "global_date_range",
    "global_company",
    "global_program",
    "global_request_status",
    "global_placement_type",
)


def _date_value(value, start: date, end: date) -> tuple[date, date]:
    if isinstance(value, tuple) and len(value) == 2:
        return value[0], value[1]
    if isinstance(value, date):
        return value, value
    return start, end


def render_global_filters(data: DashboardData) -> FilterState:
    start, end = date_bounds(data)
    with st.sidebar:
        st.markdown("## SSDC 2026")
        st.caption("Operational talent pipeline")
        st.divider()
        st.markdown("### Filters")
        selected_dates = st.date_input(
            "Date range",
            value=(start, end),
            min_value=start,
            max_value=end,
            key="global_date_range",
        )
        selected_start, selected_end = _date_value(selected_dates, start, end)
        company = st.selectbox("Company", ["All companies", *company_options(data)], key="global_company")
        program = st.selectbox("Study program", ["All study programs", *study_program_options(data)], key="global_program")
        request_status = st.selectbox(
            "Request status",
            ["All request statuses", *request_status_options(data)],
            key="global_request_status",
        )
        placement_type = st.selectbox(
            "Placement type",
            ["All placement types", *placement_type_options(data)],
            key="global_placement_type",
        )
        if st.button("Reset filters", key="reset_filters", icon=":material/refresh:", width="stretch"):
            for key in FILTER_KEYS:
                st.session_state.pop(key, None)
            st.rerun()
        st.divider()
        st.caption("Data source")
        st.code(data.source, language=None)
        st.caption("Downloadable tables reflect the active filters.")
    return FilterState(
        date_start=selected_start,
        date_end=selected_end,
        company=company,
        study_program=program,
        request_status=request_status,
        placement_type=placement_type,
    )
