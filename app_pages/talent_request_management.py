import pandas as pd
import streamlit as st

from components.chart_data import REQUEST_LABEL_COLUMN, ordered_counts, with_request_labels
from components.charts import chart_surface, render_bar, render_horizontal_bar
from components.tables import render_downloadable_table
from components.ui import analytical_columns, control_group, format_count, format_days, format_percent, render_divider, render_kpis, render_section
from app_pages.common import start_page
from config.theme import ACTION_LABEL_COLORS, ACTION_LABEL_ORDER, CHART_PRIMARY
from services.analytics import canonical_kpis, request_table


def main() -> None:
    data, filters = start_page(
        "02 / Antrean operasional",
        "Manajemen Permintaan Talenta",
        "Permintaan talenta mana yang memerlukan tindakan, dan mengapa?",
    )
    render_divider()
    requests = request_table(data, filters)
    kpis = canonical_kpis(data, filters)
    categories = ["All action labels", "Belum Dikirim", "Kurang Kandidat", "Belum Terpenuhi", "Terpenuhi", "Closed"]
    with control_group("Filter permintaan", key="request-filters"):
        category = st.selectbox("Label tindakan", categories, format_func=lambda value: {"All action labels": "Semua label tindakan", "Closed": "Ditutup"}.get(value, value), key="request_action_label")
        min_aging = st.slider("Usia minimum permintaan", 0, int(requests["aging_days"].max()) if not requests.empty else 0, 0, key="request_min_aging")
        min_gap = st.number_input("Kesenjangan minimum kebutuhan", min_value=0, value=0, step=1, key="request_min_gap")
    filtered = requests.loc[(requests["aging_days"] >= min_aging) & (requests["headcount_gap"] >= min_gap)].copy()
    if category != "All action labels":
        filtered = filtered.loc[filtered["action_label"] == category].copy()

    average_aging = filtered["aging_days"].mean() if not filtered.empty else 0
    overdue = int(filtered["overdue"].sum()) if not filtered.empty else 0
    unsent = int(filtered["action_label"].eq("Belum Dikirim").sum()) if not filtered.empty else 0
    filtered_total = len(filtered)
    share = lambda count: format_percent(count / filtered_total * 100) if filtered_total else format_percent(0)
    render_kpis([
        {
            "label": "Total permintaan talenta",
            "value": format_count(kpis["KPI-02"]),
            "help": f"Dari {format_count(kpis['KPI-01'])} perusahaan",
        },
        {
            "label": "Kebutuhan talenta",
            "value": format_count(kpis["KPI-03"]),
            "help": f"Dari {format_count(kpis['KPI-02'])} permintaan talenta",
        },
        {
            "label": "Kesenjangan kebutuhan",
            "value": format_count(kpis["KPI-10"]),
            "help": f"{format_percent(kpis['KPI-10'] / kpis['KPI-03'] * 100) if kpis['KPI-03'] else format_percent(0)} dari kebutuhan talenta",
        },
        {
            "label": "Rata-rata usia aktif",
            "value": format_days(average_aging),
            "help": f"Dari {format_count(filtered_total)} permintaan terfilter",
        },
        {
            "label": "Jumlah permintaan terlambat",
            "value": format_count(overdue),
            "help": f"{share(overdue)} dari permintaan terfilter",
        },
        {
            "label": "Jumlah permintaan belum terkirim",
            "value": format_count(unsent),
            "help": f"{share(unsent)} dari permintaan terfilter",
        },
    ], columns_per_row=6, variant="primary")

    aging = filtered.assign(
        aging_band=pd.cut(
            filtered["aging_days"], bins=[-1, 7, 14, 30, float("inf")],
            labels=["0–7 hari", "8–14 hari", "15–30 hari", ">30 hari"],
        )
    )["aging_band"].value_counts(sort=False).rename_axis("aging_band").reset_index(name="count")
    aging = aging.loc[aging["count"].gt(0)].reset_index(drop=True)
    gaps = with_request_labels(filtered.loc[filtered["headcount_gap"].gt(0)].nlargest(10, "headcount_gap"))
    supply = with_request_labels(filtered.nlargest(10, "candidate_applications"))
    action_labels = ordered_counts(filtered["action_label"], ACTION_LABEL_ORDER)
    action_labels = action_labels.rename(columns={"category": "action_label"})

    render_section("Beban permintaan", "Grafik diurutkan untuk menampilkan usia, kekurangan, dan konsentrasi prioritas.")
    left, right = analytical_columns(
        "equal",
        key="request-workload-primary",
    )
    with left:
        with chart_surface(
            "Distribusi usia permintaan",
            "Permintaan dikelompokkan berdasarkan rentang usia saat ini.",
            key="request-aging-distribution",
        ):
            render_bar(
                aging,
                "aging_band",
                "count",
                "Distribusi usia permintaan",
                show_title=False,
                series_color=CHART_PRIMARY,
                x_title="Rentang usia",
                y_title="Permintaan",
                category_order=aging["aging_band"].tolist(),
                show_legend=False,
                tick_angle=-20,
            )
    with right:
        with chart_surface(
            "Kesenjangan kebutuhan terbesar",
            "Permintaan dengan kekurangan kebutuhan talenta tersisa terbesar.",
            key="request-headcount-gaps",
        ):
            render_horizontal_bar(
                gaps,
                "headcount_gap",
                REQUEST_LABEL_COLUMN,
                "Kesenjangan kebutuhan terbesar",
                show_title=False,
                x_title="Kesenjangan kebutuhan",
                y_title="Permintaan",
            )
    left, right = analytical_columns(
        "equal",
        key="request-workload-secondary",
    )
    with left:
        with chart_surface(
            "Lamaran kandidat",
            "Permintaan diurutkan berdasarkan jumlah lamaran kandidat dan label tindakan.",
            key="request-candidate-supply",
        ):
            render_horizontal_bar(
                supply,
                "candidate_applications",
                REQUEST_LABEL_COLUMN,
                "Lamaran kandidat",
                color="action_label",
                show_title=False,
                color_map=ACTION_LABEL_COLORS,
                x_title="Lamaran",
                y_title="Permintaan",
                show_legend=False,
            )
    with right:
        with chart_surface(
            "Permintaan berdasarkan label tindakan",
            "Volume permintaan berdasarkan label operasional saat ini.",
            key="request-action-labels",
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

    render_section("Tabel tindakan", "Pilih ID permintaan untuk mempertahankannya di halaman pencocokan.")
    request_ids = ["Select a request", *filtered["id_talent_req"].tolist()]
    st.selectbox("Konteks permintaan", request_ids, format_func=lambda value: "Pilih permintaan" if value == "Select a request" else value, key="selected_request_id")
    columns = [
        "id_talent_req", "company_name", "nama_posisi", "request_status", "requested_headcount",
        "candidate_applications", "placements", "headcount_gap", "request_aging_days", "action_label",
    ]
    render_downloadable_table(filtered[columns], "ssdc-talent-requests.csv", "request-table")
    st.page_link("app_pages/talent_matching.py", label="Buka Pencocokan Talenta", icon=":material/person_search:")


if __name__ == "__main__":
    main()
