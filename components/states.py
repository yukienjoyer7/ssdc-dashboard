import streamlit as st


def render_empty(title: str, detail: str) -> None:
    st.info(f"**{title}**\n\n{detail}", icon=":material/info:")


def render_provisional_note(text: str) -> None:
    st.caption(f"Prototype logic: {text} Pending PM/Data Engineer validation.")
