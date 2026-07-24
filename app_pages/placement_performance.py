import pandas as pd
import streamlit as st

from components.charts import chart_surface, render_bar, render_histogram, render_horizontal_bar, render_line
from components.states import render_empty
from components.tables import render_downloadable_table
from components.ui import analytical_columns, format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from services.analytics import canonical_kpis, placement_table


def main() -> None:
    data, filters = start_page(
        "05 / Outcome review",
        "Placement Performance",
        "How effective is the placement process, and where do outcomes differ by company, study program, and placement type?",
        provisional_note="Canonical rate denominators are applied; dataset as-of date: {as_of_date}.",
    )
    placements = placement_table(data, filters)
    kpis = canonical_kpis(data, filters)
    render_kpis([
        {"label": "Placements", "value": format_count(kpis["KPI-06"])},
        {"label": "Placement rate", "value": format_percent(kpis["KPI-07"]), "help": "Placements / Candidate Applications"},
        {"label": "Fulfillment rate", "value": format_percent(kpis["KPI-09"]), "help": "Placements / Requested Headcount"},
    ])
    if placements.empty:
        render_empty("No placements in view", "Adjust the global filters or confirm that placement records are available.")
        return

    trend = placements.assign(month=pd.to_datetime(placements["placement_date"]).dt.to_period("M").astype(str)).groupby("month", as_index=False).size().rename(columns={"size": "placements"})
    by_company = placements["company_name"].value_counts().rename_axis("company_name").reset_index(name="placements").head(10)
    by_program = placements["study_program"].value_counts().rename_axis("study_program").reset_index(name="placements").head(10)
    by_type = placements["placement_type"].value_counts().rename_axis("placement_type").reset_index(name="placements")
    render_section("Placement outcomes", "Compare completed placement records across time and operating dimensions.")
    left, right = analytical_columns(
        "equal",
        key="placement-outcomes-primary",
    )
    with left:
        with chart_surface(
            "Placement trend",
            "Completed placements grouped by month.",
            key="placement-trend",
        ):
            render_line(trend, "month", "placements", "Placement trend", show_title=False)
    with right:
        with chart_surface(
            "Placements by company",
            "Completed placements grouped by company.",
            key="placement-company",
        ):
            render_horizontal_bar(
                by_company,
                "placements",
                "company_name",
                "Placements by company",
                show_title=False,
            )
    left, right = analytical_columns(
        "equal",
        key="placement-outcomes-secondary",
    )
    with left:
        with chart_surface(
            "Placements by study program",
            "Completed placements grouped by study program.",
            key="placement-program",
        ):
            render_horizontal_bar(
                by_program,
                "placements",
                "study_program",
                "Placements by study program",
                show_title=False,
            )
    with right:
        with chart_surface(
            "Placements by type",
            "Completed placements grouped by placement type.",
            key="placement-type",
        ):
            render_bar(
                by_type,
                "placement_type",
                "placements",
                "Placements by type",
                color="placement_type",
                show_title=False,
            )
    with chart_surface(
        "Time-to-placement distribution",
        "Elapsed days from request to completed placement.",
        key="placement-time-to-placement",
    ):
        render_histogram(
            placements,
            "time_to_placement_days",
            "Time-to-placement distribution",
            show_title=False,
        )

    render_section("Placement detail", "Download the filtered placement records for review.")
    columns = [
        "id_tracking_student", "NIM", "id_talent_req", "company_name", "position", "study_program",
        "placement_type", "placement_date", "time_to_placement_days", "progress_student",
    ]
    render_downloadable_table(placements[columns], "ssdc-placement-performance.csv", "placement-table")


if __name__ == "__main__":
    main()
