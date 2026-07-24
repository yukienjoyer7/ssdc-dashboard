import pandas as pd
import streamlit as st

from components.chart_data import monthly_counts
from components.charts import chart_surface, render_bar, render_dot_plot, render_horizontal_bar, render_insight, render_line
from components.states import render_empty
from components.tables import render_downloadable_table
from components.ui import analytical_columns, format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from config.theme import CHART_PRIMARY
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

    trend = monthly_counts({"Placements": (placements, "placement_date")}, "placements")
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
            render_line(
                trend,
                "month",
                "placements",
                "Placement trend",
                show_title=False,
                x_title="Month",
                y_title="Placements",
                x_type="category",
            )
    with right:
        with chart_surface(
            "Placements by company",
            "Completed placements grouped by company.",
            key="placement-company",
        ):
            if len(by_company) == 1:
                row = by_company.iloc[0]
                render_insight(
                    str(int(row["placements"])),
                    f"placements are with {row['company_name']}",
                    "No cross-company comparison is available in the current filtered view.",
                )
            else:
                render_horizontal_bar(
                    by_company,
                    "placements",
                    "company_name",
                    "Placements by company",
                    show_title=False,
                    x_title="Placements",
                    y_title="Company",
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
                x_title="Placements",
                y_title="Study program",
            )
    with right:
        with chart_surface(
            "Placements by type",
            "Completed placements grouped by placement type.",
            key="placement-type",
        ):
            if len(by_type) == 1:
                row = by_type.iloc[0]
                render_insight(
                    str(int(row["placements"])),
                    f"placements are {row['placement_type']}",
                    "No other placement types are present in the current filtered view.",
                )
            else:
                render_bar(
                    by_type,
                    "placement_type",
                    "placements",
                    "Placements by type",
                    color="placement_type",
                    show_title=False,
                    x_title="Placement type",
                    y_title="Placements",
                    show_legend=False,
                    tick_angle=-20,
                )
    with chart_surface(
        "Time-to-placement distribution",
        "Elapsed days from request to completed placement.",
        key="placement-time-to-placement",
    ):
        if len(placements) <= 8:
            render_dot_plot(
                placements,
                "time_to_placement_days",
                "Time-to-placement observations",
                x_title="Days to placement",
                show_title=False,
            )
        else:
            render_bar(
                placements.assign(
                    days_band=pd.cut(
                        placements["time_to_placement_days"],
                        bins=6,
                        include_lowest=True,
                    )
                ).groupby("days_band", observed=True, as_index=False).size().rename(columns={"size": "placements"}),
                "days_band",
                "placements",
                "Time-to-placement distribution",
                show_title=False,
                series_color=CHART_PRIMARY,
                x_title="Days to placement",
                y_title="Placements",
                tick_angle=-20,
            )

    render_section("Placement detail", "Download the filtered placement records for review.")
    columns = [
        "id_tracking_student", "NIM", "id_talent_req", "company_name", "position", "study_program",
        "placement_type", "placement_date", "time_to_placement_days", "progress_student",
    ]
    render_downloadable_table(placements[columns], "ssdc-placement-performance.csv", "placement-table")


if __name__ == "__main__":
    main()
