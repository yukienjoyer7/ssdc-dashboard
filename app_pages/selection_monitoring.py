import streamlit as st

from components.chart_data import ordered_counts
from components.charts import chart_surface, render_bar, render_horizontal_bar
from components.states import render_empty
from components.tables import render_downloadable_table
from components.ui import analytical_columns, control_group, format_count, render_kpis, render_section
from app_pages.common import start_page
from config.theme import CARBON_STATUS_COLORS, SELECTION_STAGE_COLORS, SELECTION_STAGE_ORDER
from services.analytics import canonical_kpis, selection_table


def main() -> None:
    data, filters = start_page(
        "04 / Follow-up queue",
        "Selection Monitoring",
        "Which candidate-selection records are stalled, overdue for follow-up, or at risk of ghosting?",
        provisional_note=(
            "Selection Aging uses dataset as-of date {as_of_date}; "
            "stale threshold remains configurable at 14 days."
        ),
    )
    selection = selection_table(data, filters)
    kpis = canonical_kpis(data, filters)
    with control_group("Filter records", key="selection-filters"):
        show_follow_up = st.checkbox("Follow-up overdue only", key="selection_follow_up_only")
        show_ghosting = st.checkbox("Ghosting cases only", key="selection_ghosting_only")
        stage_options = ["All stages", *sorted(selection["progress_student"].dropna().unique().tolist())]
        stage = st.selectbox("Current stage", stage_options, key="selection_stage")
    filtered = selection.copy()
    if show_follow_up:
        filtered = filtered.loc[filtered["follow_up_overdue"]].copy()
    if show_ghosting:
        filtered = filtered.loc[filtered["ghosting_warning"]].copy()
    if stage != "All stages":
        filtered = filtered.loc[filtered["progress_student"] == stage].copy()

    on_progress = int(filtered["canonical_outcome"].eq("On Progress").sum()) if not filtered.empty else 0
    placements = int(filtered["canonical_outcome"].eq("Placement").sum()) if not filtered.empty else 0
    rejected = int(filtered["canonical_outcome"].eq("Rejected").sum()) if not filtered.empty else 0
    ghosting = int(filtered["canonical_outcome"].eq("Ghosting").sum()) if not filtered.empty else 0
    stale = int(filtered["stale_flag"].sum()) if not filtered.empty else 0
    fu_counts = filtered["progress_student"].value_counts()
    render_kpis([
        {"label": "On Progress", "value": format_count(on_progress)},
        {"label": "Placement", "value": format_count(placements)},
        {"label": "Rejected", "value": format_count(rejected)},
        {"label": "Ghosting", "value": format_count(ghosting)},
        {"label": "Stale cases", "value": format_count(stale)},
        {"label": "FU1", "value": format_count(fu_counts.get("FU 1", 0))},
        {"label": "FU2", "value": format_count(fu_counts.get("FU 2", 0))},
        {"label": "FU3", "value": format_count(fu_counts.get("FU 3", 0))},
    ], columns_per_row=8, variant="compact")

    stages = ordered_counts(filtered["progress_student"], SELECTION_STAGE_ORDER)
    stages = stages.rename(columns={"category": "stage"})
    aging = (
        filtered.groupby("progress_student", as_index=False)["stage_aging_days"]
        .mean()
        .rename(columns={"progress_student": "stage", "stage_aging_days": "average_days"})
        .sort_values("average_days", ascending=False)
    )
    aging["average_days"] = aging["average_days"].round(1)
    risks = (
        filtered.groupby("company_name", as_index=False)[["follow_up_overdue", "ghosting_warning"]]
        .sum()
        .loc[lambda frame: frame["ghosting_warning"].gt(0)]
        .sort_values("ghosting_warning", ascending=False)
        .head(10)
    )
    render_section("Selection risk", "Use the action table to identify the record, stage, and next follow-up context.")
    left, right = analytical_columns(
        "equal",
        key="selection-risk",
    )
    with left:
        with chart_surface(
            "Selection-stage distribution",
            "Current candidate records grouped by selection stage.",
            key="selection-stage-distribution",
        ):
            render_bar(
                stages,
                "stage",
                "count",
                "Selection-stage distribution",
                color="stage",
                show_title=False,
                color_map=SELECTION_STAGE_COLORS,
                x_title="Selection stage",
                y_title="Candidates",
                category_order=stages["stage"].tolist(),
                show_legend=False,
                tick_angle=-25,
            )
    with right:
        with chart_surface(
            "Average aging by stage",
            "Mean age of records within each current stage.",
            key="selection-average-aging",
        ):
            render_horizontal_bar(
                aging,
                "average_days",
                "stage",
                "Average aging by stage",
                show_title=False,
                x_title="Average days",
                y_title="Selection stage",
                category_order=aging["stage"].tolist(),
                show_legend=False,
            )
    with chart_surface(
        "Ghosting cases by company",
        "Companies with one or more canonical ghosting outcomes.",
        key="selection-ghosting-cases",
    ):
        render_bar(
            risks,
            "company_name",
            "ghosting_warning",
            "Ghosting cases by company",
            show_title=False,
            series_color=CARBON_STATUS_COLORS["error"],
            x_title="Company",
            y_title="Ghosting cases",
            show_legend=False,
            tick_angle=-20,
        )

    render_section("Follow-up action table", "Current-stage records are shown with the source status and prototype warning flags.")
    if filtered.empty:
        render_empty("No records match", "Change the stage or warning filters to broaden the follow-up queue.")
    else:
        columns = [
            "id_tracking_student", "NIM", "student_name", "id_talent_req", "company_name", "position",
            "study_program", "progress_student", "canonical_outcome", "last_update", "selection_aging_days", "stale_flag", "ghosting_warning",
        ]
        render_downloadable_table(filtered[columns], "ssdc-selection-follow-up.csv", "selection-table")


if __name__ == "__main__":
    main()
