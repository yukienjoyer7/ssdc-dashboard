import pandas as pd
import streamlit as st


def render_downloadable_table(frame: pd.DataFrame, filename: str, key: str, height: int = 420) -> None:
    if frame.empty:
        st.info("No records match the active filters.")
        return
    st.dataframe(frame, width="stretch", hide_index=True, height=height)
    st.download_button(
        "Download filtered CSV",
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=key,
        icon=":material/download:",
    )
