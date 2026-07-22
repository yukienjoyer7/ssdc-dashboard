import streamlit as st


CARBON_CHART_COLORS = [
    "#6929c4",
    "#1192e8",
    "#005d5d",
    "#9f1853",
    "#fa4d56",
    "#198038",
    "#002d9c",
    "#ee538b",
    "#b28600",
    "#009d9a",
    "#012749",
    "#8a3800",
    "#a56eff",
]

CARBON_STATUS_COLORS = {
    "info": "#0f62fe",
    "success": "#198038",
    "warning": "#f1c21b",
    "error": "#da1e28",
}


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme: light; }
        [data-testid="stHeader"], [data-testid="stDecoration"],
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stAppViewContainer"] { background: #f4f4f4; }
        .block-container {
            max-width: none;
            padding: 5.5rem 2rem 3rem 18rem;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            font-family: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
        }
        .carbon-page-header { margin: 1rem 0 1.5rem; }
        .carbon-page-header > div:first-child {
            color: #525252;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            margin-bottom: 0.25rem;
        }
        .carbon-source {
            border-left: 3px solid #0f62fe;
            background: #ffffff;
            color: #161616;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0 1.5rem;
        }
        .carbon-source-warning { border-left-color: #f1c21b; }
        .carbon-section { margin: 2rem 0 0.75rem; }
        .carbon-chart-title {
            color: #161616;
            font-size: 0.875rem;
            font-weight: 600;
            line-height: 1.25;
            margin: 0.75rem 0 0.25rem;
        }
        @media (max-width: 48rem) {
            .block-container { padding: 4.5rem 1rem 2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
