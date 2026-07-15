import streamlit as st

from components.filters import render_global_filters
from config.theme import inject_theme
from data.loaders import load_dashboard_data


st.set_page_config(
    page_title="SSDC 2026 Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

data = load_dashboard_data()
st.session_state["global_filters"] = render_global_filters(data)

pages = [
    st.Page("pages/executive_overview.py", title="Executive Overview", icon=":material/monitoring:", default=True),
    st.Page("pages/talent_request_management.py", title="Talent Request Management", icon=":material/task_alt:"),
    st.Page("pages/talent_matching.py", title="Talent Matching", icon=":material/person_search:"),
    st.Page("pages/selection_monitoring.py", title="Selection Monitoring", icon=":material/notifications_active:"),
    st.Page("pages/placement_performance.py", title="Placement Performance", icon=":material/insights:"),
]
navigation = st.navigation(pages)
navigation.run()
