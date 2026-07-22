import streamlit as st

from ssdc_carbon_components import render_surface


st.set_page_config(page_title="Carbon component preview", layout="wide")

action = render_surface(
    "kpis",
    {
        "items": [
            {"label": "Requests", "value": "128"},
            {"label": "Placements", "value": "42", "help": "Current filtered view"},
        ]
    },
    key="preview-kpis",
)
st.write(action or "Interact with the component to emit an action.")
