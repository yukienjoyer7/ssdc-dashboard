import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ssdc-ink: #17212b;
            --ssdc-muted: #61707d;
            --ssdc-line: #dfe5e8;
            --ssdc-cyan: #087f8c;
            --ssdc-amber: #b56b00;
            --ssdc-red: #b42318;
            --ssdc-green: #18794e;
        }
        .block-container { max-width: 1440px; padding-top: 2rem; }
        [data-testid="stSidebar"] { border-right: 1px solid var(--ssdc-line); }
        [data-testid="stMetric"] {
            border: 1px solid var(--ssdc-line);
            border-radius: 6px;
            padding: 0.85rem 1rem;
            background: #ffffff;
            color: var(--ssdc-ink);
            color-scheme: light;
        }
        [data-testid="stMetric"] [data-testid="stMetricLabel"],
        [data-testid="stMetric"] [data-testid="stMetricValue"],
        [data-testid="stMetric"] [data-testid="stMetricValue"] div,
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {
            color: var(--ssdc-ink) !important;
        }
        .ssdc-kicker {
            color: var(--ssdc-cyan);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        .ssdc-source {
            border-left: 3px solid var(--ssdc-cyan);
            background: #f3f8f9;
            color: var(--ssdc-ink);
            padding: 0.65rem 0.8rem;
            margin: 0.5rem 0 1.25rem;
        }
        .ssdc-warning {
            border-left-color: var(--ssdc-amber);
            background: #fff8eb;
        }
        .ssdc-section { margin: 1.5rem 0 0.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
