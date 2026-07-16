import pandas as pd
import streamlit as st

from components.charts import render_bar, render_horizontal_bar
from components.states import render_provisional_note
from components.tables import render_downloadable_table
from components.ui import format_count, format_days, render_kpis, render_section
from pages.common import start_page
from services.analytics import canonical_kpis, request_table


def main() -> None:
    data, filters = start_page(
        "02 / Operational queue",
        "Talent Request Management",
        "Which talent requests require action, and why?",
    )
    requests = request_table(data, filters)
    kpis = canonical_kpis(data, filters)
    categories = ["All action labels", "Belum Dikirim", "Kurang Kandidat", "Belum Terpenuhi", "Terpenuhi", "Closed"]
    category = st.selectbox("Action label", categories, key="request_action_label")
    min_aging = st.slider("Minimum request aging", 0, int(requests["aging_days"].max()) if not requests.empty else 0, 0, key="request_min_aging")
    min_gap = st.number_input("Minimum headcount gap", min_value=0, value=0, step=1, key="request_min_gap")
    filtered = requests.loc[(requests["aging_days"] >= min_aging) & (requests["headcount_gap"] >= min_gap)].copy()
    if category != "All action labels":
        filtered = filtered.loc[filtered["action_label"] == category].copy()

    average_aging = filtered["aging_days"].mean() if not filtered.empty else 0
    overdue = int(filtered["overdue"].sum()) if not filtered.empty else 0
    unsent = int(filtered["action_label"].eq("Belum Dikirim").sum()) if not filtered.empty else 0
    render_kpis([
        {"label": "Total talent requests", "value": format_count(kpis["KPI-02"])},
        {"label": "Requested headcount", "value": format_count(kpis["KPI-03"])},
        {"label": "Headcount gap", "value": format_count(kpis["KPI-10"])},
        {"label": "Average active aging", "value": format_days(average_aging)},
        {"label": "Overdue request count", "value": format_count(overdue)},
        {"label": "Unsent request count", "value": format_count(unsent)},
    ])
    render_provisional_note(f"Request Aging uses dataset as-of date {kpis['as_of_date']}; action labels are deterministic and not weighted scores.")

    aging = filtered.assign(
        aging_band=pd.cut(
            filtered["aging_days"], bins=[-1, 7, 14, 30, float("inf")],
            labels=["0-7 days", "8-14 days", "15-30 days", ">30 days"],
        )
    )["aging_band"].value_counts(sort=False).rename_axis("aging_band").reset_index(name="count")
    gaps = filtered.nlargest(10, "headcount_gap").assign(label=lambda frame: frame["company_name"] + " / " + frame["nama_posisi"])
    supply = filtered.nlargest(10, "requested_headcount").assign(label=lambda frame: frame["company_name"] + " / " + frame["nama_posisi"])
    action_labels = filtered["action_label"].value_counts().rename_axis("action_label").reset_index(name="count")

    render_section("Request workload", "The charts are sorted to surface aging, shortage, and priority concentration.")
    left, right = st.columns(2)
    with left:
        render_bar(aging, "aging_band", "count", "Request aging distribution", color="aging_band")
    with right:
        render_horizontal_bar(gaps, "headcount_gap", "label", "Largest headcount gaps")
    left, right = st.columns(2)
    with left:
        render_horizontal_bar(supply, "candidate_applications", "label", "Candidate applications", color="action_label")
    with right:
        render_bar(action_labels, "action_label", "count", "Requests by action label", color="action_label")

    render_section("Action table", "Select a request ID to preserve it for the matching page.")
    request_ids = ["Select a request", *filtered["id_talent_req"].tolist()]
    selected = st.selectbox("Request context", request_ids, key="selected_request_id")
    if selected != "Select a request":
        st.session_state["selected_request_id"] = selected
    columns = [
        "id_talent_req", "company_name", "nama_posisi", "request_status", "requested_headcount",
        "candidate_applications", "placements", "headcount_gap", "request_aging_days", "action_label",
    ]
    render_downloadable_table(filtered[columns], "ssdc-talent-requests.csv", "request-table")
    st.page_link("pages/talent_matching.py", label="Open Talent Matching", icon=":material/person_search:")


if __name__ == "__main__":
    main()
