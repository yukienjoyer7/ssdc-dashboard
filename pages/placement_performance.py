import pandas as pd
import streamlit as st

from components.charts import render_bar, render_histogram, render_horizontal_bar, render_line
from components.states import render_empty, render_provisional_note
from components.tables import render_downloadable_table
from components.ui import format_count, format_days, render_kpis, render_section
from pages.common import start_page
from services.analytics import placement_table


def main() -> None:
    data, filters = start_page(
        "05 / Outcome review",
        "Placement Performance",
        "How effective is the placement process, and where do outcomes differ by company, study program, and placement type?",
    )
    placements = placement_table(data, filters)
    if placements.empty:
        render_empty("No placements in view", "Adjust the global filters or confirm that placement records are available.")
        return
    companies = placements["company_name"].nunique()
    median_time = placements["time_to_placement_days"].median()
    placement_rate = len(placements) / len(placements["NIM"].unique()) * 100 if placements["NIM"].nunique() else 0
    render_kpis([
        {"label": "Total placements", "value": format_count(len(placements))},
        {"label": "Placement rate", "value": f"{placement_rate:.1f}%", "help": "Prototype denominator: unique placed candidates"},
        {"label": "Median time to placement", "value": format_days(median_time)},
        {"label": "Companies with placements", "value": format_count(companies)},
    ])
    render_provisional_note("Placement date and duration use the current tracking record's last-update date; placement-rate denominator is provisional.")

    trend = placements.assign(month=pd.to_datetime(placements["placement_date"]).dt.to_period("M").astype(str)).groupby("month", as_index=False).size().rename(columns={"size": "placements"})
    by_company = placements["company_name"].value_counts().rename_axis("company_name").reset_index(name="placements").head(10)
    by_program = placements["study_program"].value_counts().rename_axis("study_program").reset_index(name="placements").head(10)
    by_type = placements["placement_type"].value_counts().rename_axis("placement_type").reset_index(name="placements")
    render_section("Placement outcomes", "Compare completed placement records across time and operating dimensions.")
    left, right = st.columns(2)
    with left:
        render_line(trend, "month", "placements", "Placement trend")
    with right:
        render_horizontal_bar(by_company, "placements", "company_name", "Placements by company")
    left, right = st.columns(2)
    with left:
        render_horizontal_bar(by_program, "placements", "study_program", "Placements by study program")
    with right:
        render_bar(by_type, "placement_type", "placements", "Placements by type", color="placement_type")
    render_histogram(placements, "time_to_placement_days", "Time-to-placement distribution")

    render_section("Placement detail", "Download the filtered placement records for review.")
    columns = [
        "id_tracking_student", "NIM", "id_talent_req", "company_name", "position", "study_program",
        "placement_type", "placement_date", "time_to_placement_days", "progress_student",
    ]
    render_downloadable_table(placements[columns], "ssdc-placement-performance.csv", "placement-table")


if __name__ == "__main__":
    main()
