import streamlit as st

from components.chart_data import REQUEST_LABEL_COLUMN, monthly_counts, ordered_counts, with_request_labels
from components.charts import chart_surface, render_bar, render_horizontal_bar, render_line
from components.tables import render_downloadable_table
from components.ui import analytical_columns, format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from config.theme import (
    ACTION_LABEL_COLORS,
    ACTION_LABEL_ORDER,
    CHART_PRIMARY,
    EXECUTIVE_OVERVIEW_SERIES_COLORS,
    SELECTION_STAGE_ORDER,
)
from services.analytics import canonical_kpis, request_table, selection_table, placement_table


def main() -> None:
    data, filters = start_page(
        "01 / Command view",
        "Executive Overview",
        "What is the current overall condition of talent demand, fulfilment, selection activity, and placement outcomes?",
        provisional_note="Canonical KPI preview; dataset as-of date: {as_of_date}.",
    )
    requests = request_table(data, filters)
    selection = selection_table(data, filters)
    placements = placement_table(data, filters)
    kpis = canonical_kpis(data, filters)
    actions = requests.loc[requests["action_label"].isin(["Belum Dikirim", "Kurang Kandidat", "Belum Terpenuhi"])].copy()
    ghosting_cases = int(selection["canonical_outcome"].eq("Ghosting").sum())

    render_kpis(
        [
            {
                "label": "Requested headcount",
                "value": format_count(kpis["KPI-03"]),
                "help": f"Across {format_count(kpis['KPI-02'])} talent requests",
            },
            {
                "label": "Placements",
                "value": format_count(kpis["KPI-06"]),
                "help": f"{format_percent(kpis['KPI-09'])} of requested headcount",
            },
            {
                "label": "Placement rate",
                "value": format_percent(kpis["KPI-07"]),
                "help": (
                    f"{format_count(kpis['KPI-06'])} placements from "
                    f"{format_count(kpis['KPI-04'])} applications"
                ),
            },
            {
                "label": "Ghosting rate",
                "value": format_percent(kpis["KPI-08"]),
                "help": (
                    f"{format_count(ghosting_cases)} ghosting cases from "
                    f"{format_count(kpis['KPI-04'])} applications"
                ),
            },
        ],
        columns_per_row=4,
        variant="primary",
        section_label="Primary outcomes",
        key="executive-primary-outcomes",
    )
    render_kpis(
        [
            {"label": "Total companies", "value": format_count(kpis["KPI-01"])},
            {"label": "Total talent requests", "value": format_count(kpis["KPI-02"])},
            {"label": "Candidate applications", "value": format_count(kpis["KPI-04"])},
            {"label": "Unique candidates", "value": format_count(kpis["KPI-05"])},
        ],
        columns_per_row=4,
        variant="secondary",
        section_label="Pipeline volume",
        key="executive-pipeline-volume",
    )

    trend = monthly_counts(
        {
            "Talent requests": (requests, "request_date"),
            "Placements": (placements, "placement_date"),
        },
        "count",
    )
    stage_counts = ordered_counts(selection["progress_student"], SELECTION_STAGE_ORDER)
    stage_counts = stage_counts.rename(columns={"category": "stage"})
    gap = with_request_labels(requests.loc[requests["headcount_gap"].gt(0)].nlargest(8, "headcount_gap"))
    action_labels = ordered_counts(requests["action_label"], ACTION_LABEL_ORDER)
    action_labels = action_labels.rename(columns={"category": "action_label"})

    render_section("Pipeline movement", "Request and placement events by month.")
    left, right = analytical_columns(
        "main_supporting",
        key="overview-pipeline-movement",
    )
    with left:
        with chart_surface(
            "Talent requests and placements",
            "Monthly movement of talent requests and completed placements.",
            key="overview-request-placement-trend",
        ):
            render_line(
                trend,
                "month",
                "count",
                "Talent requests and placements",
                color="metric",
                show_title=False,
                color_map=EXECUTIVE_OVERVIEW_SERIES_COLORS,
                x_title="Month",
                y_title="Records",
                x_type="category",
            )
    with right:
        with chart_surface(
            "Current selection-stage distribution",
            "Candidate records grouped by their current selection stage.",
            key="overview-selection-stage",
        ):
            render_horizontal_bar(
                stage_counts,
                "count",
                "stage",
                "Current selection-stage distribution",
                show_title=False,
                series_color=CHART_PRIMARY,
                x_title="Candidates",
                y_title="Selection stage",
                category_order=stage_counts["stage"].tolist(),
                show_legend=False,
            )

    left, right = analytical_columns(
        "equal",
        key="overview-secondary-analysis",
    )
    with left:
        with chart_surface(
            "Largest fulfilment gaps",
            "Requests with the largest remaining headcount shortfall.",
            key="overview-fulfilment-gaps",
        ):
            render_horizontal_bar(
                gap,
                "headcount_gap",
                REQUEST_LABEL_COLUMN,
                "Largest fulfilment gaps",
                show_title=False,
                x_title="Headcount gap",
                y_title="Request",
            )
    with right:
        with chart_surface(
            "Requests by action label",
            "Request volume grouped by its current action label.",
            key="overview-action-labels",
        ):
            render_bar(
                action_labels,
                "action_label",
                "count",
                "Requests by action label",
                color="action_label",
                show_title=False,
                color_map=ACTION_LABEL_COLORS,
                x_title="Action label",
                y_title="Requests",
                category_order=action_labels["action_label"].tolist(),
                show_legend=False,
                tick_angle=-25,
            )

    render_section("Requests requiring action", "Use the request-management page to inspect the reason and next operational step.")
    action_columns = [
        "id_talent_req", "company_name", "nama_posisi", "requested_headcount", "placements",
        "headcount_gap", "request_aging_days", "action_label",
    ]
    render_downloadable_table(actions[action_columns], "ssdc-action-requests.csv", "overview-actions")
    st.page_link("app_pages/talent_request_management.py", label="Open Talent Request Management", icon=":material/arrow_forward:")


if __name__ == "__main__":
    main()
