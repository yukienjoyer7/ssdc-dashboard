import pandas as pd
import streamlit as st

from components.charts import render_bar, render_horizontal_bar, render_line
from components.states import render_provisional_note
from components.tables import render_downloadable_table
from components.ui import format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from services.analytics import canonical_kpis, request_table, selection_table, placement_table


def main() -> None:
    data, filters = start_page(
        "01 / Command view",
        "Executive Overview",
        "What is the current overall condition of talent demand, fulfilment, selection activity, and placement outcomes?",
    )
    requests = request_table(data, filters)
    selection = selection_table(data, filters)
    placements = placement_table(data, filters)
    kpis = canonical_kpis(data, filters)
    actions = requests.loc[requests["action_label"].isin(["Belum Dikirim", "Kurang Kandidat", "Belum Terpenuhi"])].copy()

    render_kpis([
        {"label": "Total companies", "value": format_count(kpis["KPI-01"])},
        {"label": "Total talent requests", "value": format_count(kpis["KPI-02"])},
        {"label": "Requested headcount", "value": format_count(kpis["KPI-03"])},
        {"label": "Candidate applications", "value": format_count(kpis["KPI-04"])},
        {"label": "Unique candidates", "value": format_count(kpis["KPI-05"])},
        {"label": "Placements", "value": format_count(kpis["KPI-06"])},
        {"label": "Placement rate", "value": format_percent(kpis["KPI-07"])},
        {"label": "Ghosting rate", "value": format_percent(kpis["KPI-08"])},
    ], columns_per_row=4)
    render_provisional_note(f"Canonical KPI preview; dataset as-of date: {kpis['as_of_date']}.")

    trend_requests = requests.assign(month=pd.to_datetime(requests["request_date"]).dt.to_period("M").astype(str)).groupby("month", as_index=False).size().rename(columns={"size": "count"})
    trend_placements = placements.assign(month=pd.to_datetime(placements["placement_date"]).dt.to_period("M").astype(str)).groupby("month", as_index=False).size().rename(columns={"size": "count"})
    trend = pd.concat([
        trend_requests.assign(metric="Talent requests"),
        trend_placements.assign(metric="Placements"),
    ], ignore_index=True)
    stage_counts = selection["progress_student"].value_counts().rename_axis("stage").reset_index(name="count")
    gap = requests.nlargest(8, "headcount_gap").assign(label=lambda frame: frame["company_name"] + " / " + frame["nama_posisi"])
    action_labels = requests["action_label"].value_counts().rename_axis("action_label").reset_index(name="count")

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
        render_bar(action_labels, "action_label", "count", "Requests by action label", color="action_label")

    render_section("Requests requiring action", "Use the request-management page to inspect the reason and next operational step.")
    action_columns = [
        "id_talent_req", "company_name", "nama_posisi", "requested_headcount", "placements",
        "headcount_gap", "request_aging_days", "action_label",
    ]
    render_downloadable_table(actions[action_columns], "ssdc-action-requests.csv", "overview-actions")
    st.page_link("app_pages/talent_request_management.py", label="Open Talent Request Management", icon=":material/arrow_forward:")


if __name__ == "__main__":
    main()
