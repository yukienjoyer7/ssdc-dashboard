import pandas as pd
import streamlit as st

from components.charts import render_bar, render_horizontal_bar, render_line
from components.states import render_provisional_note
from components.tables import render_downloadable_table
from components.ui import format_count, format_percent, render_kpis, render_section
from pages.common import start_page
from services.analytics import request_table, selection_table, placement_table


def main() -> None:
    data, filters = start_page(
        "01 / Command view",
        "Executive Overview",
        "What is the current overall condition of talent demand, fulfilment, selection activity, and placement outcomes?",
    )
    requests = request_table(data, filters)
    selection = selection_table(data, filters)
    placements = placement_table(data, filters)
    active = requests.loc[~requests["request_status"].isin(["Closed", "Draft"])]
    requested_headcount = requests["requested_headcount"].sum()
    fulfilled_headcount = requests["fulfilled_headcount"].sum()
    fulfilment_rate = fulfilled_headcount / requested_headcount * 100 if requested_headcount else 0
    active_selection = selection.loc[~selection["progress_student"].isin(["Rejected", "Finish", "Placement"])]
    actions = requests.loc[requests["priority_category"].isin(["Action", "Urgent"])].copy()

    render_kpis([
        {"label": "Active talent requests", "value": format_count(len(active)), "help": "Prototype active-status mapping"},
        {"label": "Requested headcount", "value": format_count(requested_headcount)},
        {"label": "Fulfilled headcount", "value": format_count(fulfilled_headcount), "help": "Placement records linked to requests"},
        {"label": "Fulfilment rate", "value": format_percent(fulfilment_rate)},
        {"label": "Candidates in selection", "value": format_count(len(active_selection))},
        {"label": "Successful placements", "value": format_count(len(placements))},
    ])
    render_provisional_note("Active status, fulfilment, and placement linkage follow the current six-table preview contract.")

    trend_requests = requests.assign(month=pd.to_datetime(requests["request_date"]).dt.to_period("M").astype(str)).groupby("month", as_index=False).size().rename(columns={"size": "count"})
    trend_placements = placements.assign(month=pd.to_datetime(placements["placement_date"]).dt.to_period("M").astype(str)).groupby("month", as_index=False).size().rename(columns={"size": "count"})
    trend = pd.concat([
        trend_requests.assign(metric="Talent requests"),
        trend_placements.assign(metric="Placements"),
    ], ignore_index=True)
    stage_counts = selection["progress_student"].value_counts().rename_axis("stage").reset_index(name="count")
    gap = requests.nlargest(8, "headcount_gap").assign(label=lambda frame: frame["company_name"] + " / " + frame["nama_posisi"])
    priority = requests["priority_category"].value_counts().rename_axis("priority").reset_index(name="count")

    render_section("Pipeline movement", "Request and placement events by month.")
    left, right = st.columns(2)
    with left:
        render_line(trend, "month", "count", "Talent requests and placements", color="metric")
    with right:
        render_horizontal_bar(stage_counts, "count", "stage", "Current selection-stage distribution")

    left, right = st.columns(2)
    with left:
        render_horizontal_bar(gap, "headcount_gap", "label", "Largest fulfilment gaps")
    with right:
        render_bar(priority, "priority", "count", "Requests by prototype priority", color="priority")

    render_section("Requests requiring action", "Use the request-management page to inspect the reason and next operational step.")
    action_columns = [
        "id_talent_req", "company_name", "nama_posisi", "requested_headcount", "fulfilled_headcount",
        "headcount_gap", "aging_days", "priority_category", "priority_reason",
    ]
    render_downloadable_table(actions[action_columns], "ssdc-action-requests.csv", "overview-actions")
    st.page_link("pages/talent_request_management.py", label="Open Talent Request Management", icon=":material/arrow_forward:")


if __name__ == "__main__":
    main()
