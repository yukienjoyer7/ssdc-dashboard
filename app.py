import streamlit as st

from components.carbon_ui import (
    PAGE_SPECS,
    default_filters,
    page_spec_for_slug,
    page_spec_for_title,
    render_filter_toolbar,
    render_shell,
)
from config.theme import inject_theme
from data.loaders import load_dashboard_data


st.set_page_config(
    page_title="SSDC 2026 Dashboard",
    page_icon=":material/monitoring:",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

data = load_dashboard_data()
pages = [
    st.Page(
        page.path,
        title=page.title,
        icon=f":material/{page.icon}:",
        default=index == 0,
    )
    for index, page in enumerate(PAGE_SPECS)
]
navigation = st.navigation(pages, position="hidden")
active_page = page_spec_for_title(getattr(navigation, "title", PAGE_SPECS[0].title))

shell_action = render_shell(active_page.slug)
if shell_action and shell_action.get("type") == "navigate":
    target = page_spec_for_slug(str(shell_action.get("page", "")))
    if target:
        st.switch_page(target.path)

current_filters = st.session_state.get("global_filters")
if current_filters is None:
    current_filters = default_filters(data)
st.session_state["global_filters"] = render_filter_toolbar(data, current_filters)

navigation.run()
