import streamlit as st

from components.chart_data import ordered_counts
from components.charts import chart_surface, render_bar, render_horizontal_bar
from components.states import render_empty
from components.tables import render_downloadable_table
from components.ui import analytical_columns, control_group, format_count, format_percent, render_kpis, render_section
from app_pages.common import start_page
from config.theme import CARBON_STATUS_COLORS, SELECTION_STAGE_COLORS, SELECTION_STAGE_ORDER
from services.analytics import canonical_kpis, selection_table


def main() -> None:
    data, filters = start_page(
        "04 / Antrean tindak lanjut",
        "Pemantauan Seleksi",
        "Catatan seleksi kandidat mana yang terhenti, terlambat ditindaklanjuti, atau berisiko ghosting?",
        provisional_note=(
            "Usia Seleksi menggunakan tanggal data {as_of_date}; "
            "ambang kedaluwarsa tetap dapat diatur pada 14 hari."
        ),
    )
    selection = selection_table(data, filters)
    kpis = canonical_kpis(data, filters)
    with control_group("Filter catatan", key="selection-filters"):
        show_follow_up = st.checkbox("Hanya tindak lanjut yang terlambat", key="selection_follow_up_only")
        show_ghosting = st.checkbox("Hanya kasus ghosting", key="selection_ghosting_only")
        stage_options = ["All stages", *sorted(selection["progress_student"].dropna().unique().tolist())]
        stage = st.selectbox("Tahap saat ini", stage_options, format_func=lambda value: "Semua tahap" if value == "All stages" else value, key="selection_stage")
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
    total = len(filtered)
    share = lambda count: format_percent(count / total * 100) if total else format_percent(0)
    render_kpis([
        {"label": "Dalam proses", "value": format_count(on_progress), "help": f"{share(on_progress)} dari catatan"},
        {"label": "Penempatan", "value": format_count(placements), "help": f"{share(placements)} dari catatan"},
        {"label": "Ditolak", "value": format_count(rejected), "help": f"{share(rejected)} dari catatan"},
        {"label": "Ghosting", "value": format_count(ghosting), "help": f"{share(ghosting)} dari catatan"},
        {"label": "Kasus kedaluwarsa", "value": format_count(stale), "help": f"{share(stale)} dari catatan"},
        {"label": "TL 1", "value": format_count(fu_counts.get("FU 1", 0)), "help": f"{share(fu_counts.get('FU 1', 0))} dari catatan"},
        {"label": "TL 2", "value": format_count(fu_counts.get("FU 2", 0)), "help": f"{share(fu_counts.get('FU 2', 0))} dari catatan"},
        {"label": "TL 3", "value": format_count(fu_counts.get("FU 3", 0)), "help": f"{share(fu_counts.get('FU 3', 0))} dari catatan"},
    ], columns_per_row=8, variant="primary")

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
    render_section("Risiko seleksi", "Gunakan tabel tindakan untuk mengidentifikasi catatan, tahap, dan konteks tindak lanjut berikutnya.")
    left, right = analytical_columns(
        "equal",
        key="selection-risk",
    )
    with left:
        with chart_surface(
            "Distribusi tahap seleksi",
            "Catatan kandidat saat ini dikelompokkan berdasarkan tahap seleksi.",
            key="selection-stage-distribution",
        ):
            render_bar(
                stages,
                "stage",
                "count",
                "Distribusi tahap seleksi",
                color="stage",
                show_title=False,
                color_map=SELECTION_STAGE_COLORS,
                x_title="Tahap seleksi",
                y_title="Kandidat",
                category_order=stages["stage"].tolist(),
                show_legend=False,
                tick_angle=-25,
            )
    with right:
        with chart_surface(
            "Rata-rata usia berdasarkan tahap",
            "Rata-rata usia catatan dalam setiap tahap saat ini.",
            key="selection-average-aging",
        ):
            render_horizontal_bar(
                aging,
                "average_days",
                "stage",
                "Rata-rata usia berdasarkan tahap",
                show_title=False,
                x_title="Rata-rata hari",
                y_title="Tahap seleksi",
                category_order=aging["stage"].tolist(),
                show_legend=False,
            )
    with chart_surface(
        "Kasus ghosting berdasarkan perusahaan",
        "Perusahaan dengan satu atau lebih hasil ghosting kanonis.",
        key="selection-ghosting-cases",
    ):
        render_bar(
            risks,
            "company_name",
            "ghosting_warning",
            "Kasus ghosting berdasarkan perusahaan",
            show_title=False,
            series_color=CARBON_STATUS_COLORS["error"],
            x_title="Perusahaan",
            y_title="Kasus ghosting",
            show_legend=False,
            tick_angle=-20,
        )

    render_section("Tabel tindakan tindak lanjut", "Catatan tahap saat ini ditampilkan bersama status sumber dan penanda peringatan prototipe.")
    if filtered.empty:
        render_empty("Tidak ada catatan yang cocok", "Ubah tahap atau filter peringatan untuk memperluas antrean tindak lanjut.")
    else:
        columns = [
            "id_tracking_student", "NIM", "student_name", "id_talent_req", "company_name", "position",
            "study_program", "progress_student", "canonical_outcome", "last_update", "selection_aging_days", "stale_flag", "ghosting_warning",
        ]
        render_downloadable_table(filtered[columns], "ssdc-selection-follow-up.csv", "selection-table")


if __name__ == "__main__":
    main()
