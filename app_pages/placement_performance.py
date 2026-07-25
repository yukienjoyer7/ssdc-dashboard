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
        "05 / Tinjauan hasil",
        "Kinerja Penempatan",
        "Seberapa efektif proses penempatan, dan di mana hasilnya berbeda berdasarkan perusahaan, program studi, dan jenis penempatan?",
        provisional_note="Penyebut tingkat kanonis diterapkan; tanggal data: {as_of_date}.",
    )
    placements = placement_table(data, filters)
    kpis = canonical_kpis(data, filters)
    render_kpis([
        {"label": "Penempatan", "value": format_count(kpis["KPI-06"])},
        {"label": "Tingkat penempatan", "value": format_percent(kpis["KPI-07"]), "help": "Penempatan / Lamaran Kandidat"},
        {"label": "Tingkat pemenuhan", "value": format_percent(kpis["KPI-09"]), "help": "Penempatan / Kebutuhan Talenta"},
    ])
    if placements.empty:
        render_empty("Tidak ada penempatan pada tampilan", "Sesuaikan filter global atau pastikan catatan penempatan tersedia.")
        return

    trend = monthly_counts({"Penempatan": (placements, "placement_date")}, "placements")
    by_company = placements["company_name"].value_counts().rename_axis("company_name").reset_index(name="placements").head(10)
    by_program = placements["study_program"].value_counts().rename_axis("study_program").reset_index(name="placements").head(10)
    by_type = placements["placement_type"].value_counts().rename_axis("placement_type").reset_index(name="placements")
    render_section("Hasil penempatan", "Bandingkan catatan penempatan selesai berdasarkan waktu dan dimensi operasional.")
    left, right = analytical_columns(
        "equal",
        key="placement-outcomes-primary",
    )
    with left:
        with chart_surface(
            "Tren penempatan",
            "Penempatan selesai dikelompokkan per bulan.",
            key="placement-trend",
        ):
            render_line(
                trend,
                "month",
                "placements",
                "Tren penempatan",
                show_title=False,
                x_title="Bulan",
                y_title="Penempatan",
                x_type="category",
            )
    with right:
        with chart_surface(
            "Penempatan berdasarkan perusahaan",
            "Penempatan selesai dikelompokkan berdasarkan perusahaan.",
            key="placement-company",
        ):
            if len(by_company) == 1:
                row = by_company.iloc[0]
                render_insight(
                    str(int(row["placements"])),
                    f"penempatan berada di {row['company_name']}",
                    "Tidak ada perbandingan antarperusahaan pada tampilan terfilter saat ini.",
                )
            else:
                render_horizontal_bar(
                    by_company,
                    "placements",
                    "company_name",
                    "Penempatan berdasarkan perusahaan",
                    show_title=False,
                    x_title="Penempatan",
                    y_title="Perusahaan",
                )
    left, right = analytical_columns(
        "equal",
        key="placement-outcomes-secondary",
    )
    with left:
        with chart_surface(
            "Penempatan berdasarkan program studi",
            "Penempatan selesai dikelompokkan berdasarkan program studi.",
            key="placement-program",
        ):
            render_horizontal_bar(
                by_program,
                "placements",
                "study_program",
                "Penempatan berdasarkan program studi",
                show_title=False,
                x_title="Penempatan",
                y_title="Program studi",
            )
    with right:
        with chart_surface(
            "Penempatan berdasarkan jenis",
            "Penempatan selesai dikelompokkan berdasarkan jenis penempatan.",
            key="placement-type",
        ):
            if len(by_type) == 1:
                row = by_type.iloc[0]
                render_insight(
                    str(int(row["placements"])),
                    f"penempatan berjenis {row['placement_type']}",
                    "Tidak ada jenis penempatan lain pada tampilan terfilter saat ini.",
                )
            else:
                render_bar(
                    by_type,
                    "placement_type",
                    "placements",
                    "Penempatan berdasarkan jenis",
                    color="placement_type",
                    show_title=False,
                    x_title="Jenis penempatan",
                    y_title="Penempatan",
                    show_legend=False,
                    tick_angle=-20,
                )
    with chart_surface(
        "Distribusi waktu hingga penempatan",
        "Hari yang berlalu dari permintaan hingga penempatan selesai.",
        key="placement-time-to-placement",
    ):
        if len(placements) <= 8:
            render_dot_plot(
                placements,
                "time_to_placement_days",
                "Observasi waktu hingga penempatan",
                x_title="Hari hingga penempatan",
                show_title=False,
            )
        else:
            frame = placements.assign(
                days_band=pd.cut(
                    placements["time_to_placement_days"],
                    bins=6,
                    include_lowest=True,
                )
            ).groupby("days_band", observed=True, as_index=False).size().rename(columns={"size": "placements"})
            frame["days_band"] = frame["days_band"].astype(str)
            render_bar(
                frame,
                "days_band",
                "placements",
                "Distribusi waktu hingga penempatan",
                show_title=False,
                series_color=CHART_PRIMARY,
                x_title="Hari hingga penempatan",
                y_title="Penempatan",
                tick_angle=-20,
            )

    render_section("Detail penempatan", "Unduh catatan penempatan terfilter untuk ditinjau.")
    columns = [
        "id_tracking_student", "NIM", "id_talent_req", "company_name", "position", "study_program",
        "placement_type", "placement_date", "time_to_placement_days", "progress_student",
    ]
    render_downloadable_table(placements[columns], "ssdc-placement-performance.csv", "placement-table")


if __name__ == "__main__":
    main()
