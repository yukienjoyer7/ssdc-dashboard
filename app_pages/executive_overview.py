import streamlit as st

from components.chart_data import REQUEST_LABEL_COLUMN, monthly_counts, ordered_counts, with_request_labels
from components.charts import chart_surface, render_bar, render_horizontal_bar, render_line
from components.tables import render_downloadable_table
from components.ui import analytical_columns, format_count, format_percent, render_divider, render_kpis, render_section
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
        "01 / Tampilan ringkasan",
        "Ringkasan Eksekutif",
        "Bagaimana kondisi terkini permintaan talenta, pemenuhan, aktivitas seleksi, dan hasil penempatan?",
    )
    render_divider()
    requests = request_table(data, filters)
    selection = selection_table(data, filters)
    placements = placement_table(data, filters)
    kpis = canonical_kpis(data, filters)
    actions = requests.loc[requests["action_label"].isin(["Belum Dikirim", "Kurang Kandidat", "Belum Terpenuhi"])].copy()
    ghosting_cases = int(selection["canonical_outcome"].eq("Ghosting").sum())

    render_kpis(
        [
            {
                "label": "Kebutuhan talenta",
                "value": format_count(kpis["KPI-03"]),
                "help": f"Dari {format_count(kpis['KPI-02'])} permintaan talenta",
            },
            {
                "label": "Penempatan",
                "value": format_count(kpis["KPI-06"]),
                "help": f"{format_percent(kpis['KPI-09'])} dari kebutuhan talenta",
            },
            {
                "label": "Tingkat penempatan",
                "value": format_percent(kpis["KPI-07"]),
                "help": (
                    f"{format_count(kpis['KPI-06'])} penempatan dari "
                    f"{format_count(kpis['KPI-04'])} lamaran"
                ),
            },
            {
                "label": "Tingkat ghosting",
                "value": format_percent(kpis["KPI-08"]),
                "help": (
                    f"{format_count(ghosting_cases)} kasus ghosting dari "
                    f"{format_count(kpis['KPI-04'])} lamaran"
                ),
            },
        ],
        columns_per_row=4,
        variant="primary",
        section_label="Hasil utama",
        key="executive-primary-outcomes",
    )
    render_kpis(
        [
            {"label": "Total perusahaan", "value": format_count(kpis["KPI-01"])},
            {"label": "Total permintaan talenta", "value": format_count(kpis["KPI-02"])},
            {"label": "Lamaran kandidat", "value": format_count(kpis["KPI-04"])},
            {"label": "Kandidat unik", "value": format_count(kpis["KPI-05"])},
        ],
        columns_per_row=4,
        variant="secondary",
        section_label="Volume proses",
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

    render_section("Pergerakan proses", "Peristiwa permintaan dan penempatan per bulan.")
    left, right = analytical_columns(
        "main_supporting",
        key="overview-pipeline-movement",
    )
    with left:
        with chart_surface(
            "Permintaan talenta dan penempatan",
            "Pergerakan bulanan permintaan talenta dan penempatan selesai.",
            key="overview-request-placement-trend",
        ):
            render_line(
                trend,
                "month",
                "count",
                "Permintaan talenta dan penempatan",
                color="metric",
                show_title=False,
                color_map=EXECUTIVE_OVERVIEW_SERIES_COLORS,
                x_title="Bulan",
                y_title="Catatan",
                x_type="category",
            )
    with right:
        with chart_surface(
            "Distribusi tahap seleksi saat ini",
            "Catatan kandidat dikelompokkan berdasarkan tahap seleksi saat ini.",
            key="overview-selection-stage",
        ):
            render_horizontal_bar(
                stage_counts,
                "count",
                "stage",
                "Distribusi tahap seleksi saat ini",
                show_title=False,
                series_color=CHART_PRIMARY,
                x_title="Kandidat",
                y_title="Tahap seleksi",
                category_order=stage_counts["stage"].tolist(),
                show_legend=False,
            )

    left, right = analytical_columns(
        "equal",
        key="overview-secondary-analysis",
    )
    with left:
        with chart_surface(
            "Kesenjangan pemenuhan terbesar",
            "Permintaan dengan kekurangan kebutuhan talenta tersisa terbesar.",
            key="overview-fulfilment-gaps",
        ):
            render_horizontal_bar(
                gap,
                "headcount_gap",
                REQUEST_LABEL_COLUMN,
                "Kesenjangan pemenuhan terbesar",
                show_title=False,
                x_title="Kesenjangan kebutuhan",
                y_title="Permintaan",
            )
    with right:
        with chart_surface(
            "Permintaan berdasarkan label tindakan",
            "Volume permintaan berdasarkan label tindakan saat ini.",
            key="overview-action-labels",
        ):
            render_bar(
                action_labels,
                "action_label",
                "count",
                "Permintaan berdasarkan label tindakan",
                color="action_label",
                show_title=False,
                color_map=ACTION_LABEL_COLORS,
                x_title="Label tindakan",
                y_title="Permintaan",
                category_order=action_labels["action_label"].tolist(),
                show_legend=False,
                tick_angle=-25,
            )

    render_section("Permintaan yang memerlukan tindakan", "Gunakan halaman manajemen permintaan untuk meninjau alasan dan langkah operasional berikutnya.")
    action_columns = [
        "id_talent_req", "company_name", "nama_posisi", "requested_headcount", "placements",
        "headcount_gap", "request_aging_days", "action_label",
    ]
    render_downloadable_table(actions[action_columns], "ssdc-action-requests.csv", "overview-actions")
    st.page_link("app_pages/talent_request_management.py", label="Buka Manajemen Permintaan Talenta", icon=":material/arrow_forward:")


if __name__ == "__main__":
    main()
