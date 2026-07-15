import streamlit as st

from components.charts import render_bar, render_horizontal_bar
from components.states import render_empty, render_provisional_note
from components.tables import render_downloadable_table
from components.ui import format_count, format_days, render_kpis, render_section
from pages.common import start_page
from services.analytics import selection_table


def main() -> None:
    data, filters = start_page(
        "04 / Follow-up queue",
        "Selection Monitoring",
        "Which candidate-selection records are stalled, overdue for follow-up, or at risk of ghosting?",
    )
    selection = selection_table(data, filters)
    show_follow_up = st.checkbox("Follow-up overdue only", key="selection_follow_up_only")
    show_ghosting = st.checkbox("Ghosting warning only", key="selection_ghosting_only")
    stage_options = ["All stages", *sorted(selection["progress_student"].dropna().unique().tolist())]
    stage = st.selectbox("Current stage", stage_options, key="selection_stage")
    filtered = selection.copy()
    if show_follow_up:
        filtered = filtered.loc[filtered["follow_up_overdue"]].copy()
    if show_ghosting:
        filtered = filtered.loc[filtered["ghosting_warning"]].copy()
    if stage != "All stages":
        filtered = filtered.loc[filtered["progress_student"] == stage].copy()

    active = filtered.loc[~filtered["progress_student"].isin(["Rejected", "Finish", "Placement"])]
    average_aging = active["stage_aging_days"].mean() if not active.empty else 0
    overdue = int(filtered["follow_up_overdue"].sum()) if not filtered.empty else 0
    ghosting = int(filtered["ghosting_warning"].sum()) if not filtered.empty else 0
    median_duration = filtered["stage_aging_days"].median() if not filtered.empty else 0
    render_kpis([
        {"label": "Active selection", "value": format_count(len(active))},
        {"label": "Average stage aging", "value": format_days(average_aging)},
        {"label": "Follow-up overdue", "value": format_count(overdue)},
        {"label": "Ghosting warning", "value": format_count(ghosting)},
        {"label": "Median selection duration", "value": format_days(median_duration)},
    ])
    render_provisional_note("Stage aging uses last-update dates; ghosting uses the source status plus a 14-day follow-up proxy.")

    stages = filtered["progress_student"].value_counts().rename_axis("stage").reset_index(name="count")
    aging = filtered.groupby("progress_student", as_index=False)["stage_aging_days"].mean().rename(columns={"progress_student": "stage", "stage_aging_days": "average_days"}).sort_values("average_days")
    risks = filtered.groupby("company_name", as_index=False)[["follow_up_overdue", "ghosting_warning"]].sum().sort_values("ghosting_warning", ascending=False).head(10)
    render_section("Selection risk", "Use the action table to identify the record, stage, and next follow-up context.")
    left, right = st.columns(2)
    with left:
        render_bar(stages, "stage", "count", "Selection-stage distribution", color="stage")
    with right:
        render_horizontal_bar(aging, "average_days", "stage", "Average aging by stage")
    render_bar(risks, "company_name", "ghosting_warning", "Ghosting warnings by company", color="company_name")

    render_section("Follow-up action table", "Current-stage records are shown with the source status and prototype warning flags.")
    if filtered.empty:
        render_empty("No records match", "Change the stage or warning filters to broaden the follow-up queue.")
    else:
        columns = [
            "id_tracking_student", "NIM", "student_name", "id_talent_req", "company_name", "position",
            "study_program", "progress_student", "last_update", "stage_aging_days", "follow_up_overdue", "ghosting_warning",
        ]
        render_downloadable_table(filtered[columns], "ssdc-selection-follow-up.csv", "selection-table")


if __name__ == "__main__":
    main()
