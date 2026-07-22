import pandas as pd
import streamlit as st

from components.carbon_ui import render_table


def render_downloadable_table(frame: pd.DataFrame, filename: str, key: str, height: int = 420) -> None:
    columns = [(column, column.replace("_", " ").title()) for column in frame.columns]
    render_table(frame, columns=columns, key=f"{key}-carbon")
    if frame.empty:
        return
    st.download_button(
        "Download filtered CSV",
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=key,
        icon=":material/download:",
    )
