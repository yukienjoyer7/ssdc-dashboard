import pandas as pd
import streamlit as st

from components.chart_data import REQUEST_LABEL_COLUMN, ordered_counts, with_request_labels
from components.charts import chart_surface, render_bar, render_horizontal_bar
from components.tables import render_downloadable_table
from components.ui import analytical_columns, control_group, format_count, format_days, render_kpis, render_section
from app_pages.common import start_page
from config.theme import ACTION_LABEL_COLORS, ACTION_LABEL_ORDER, CHART_PRIMARY
from services.analytics import canonical_kpis, request_table


def main() -> None:
    data, filters = start_page(
        "02 / Operational queue",
        "Talent Request Management",
        "Which talent requests require action, and why?",
        provisional_note=(
            "Request Aging uses dataset as-of date {as_of_date}; "
            "action labels are deterministic and not weighted scores."
        ),
    )
    requests = request_table(data, filters)
    kpis = canonical_kpis(data, filters)
    categories = ["All action labels", "Belum Dikirim", "Kurang Kandidat", "Belum Terpenuhi", "Terpenuhi", "Closed"]
    with control_group("Filter requests", key="request-filters"):
        category = st.selectbox("Action label", categories, key="request_action_label")
        min_aging = st.slider("Minimum request aging", 0, int(requests["aging_days"].max()) if not requests.empty else 0, 0, key="request_min_aging")
        min_gap = st.number_input("Minimum headcount gap", min_value=0, value=0, step=1, key="request_min_gap")
    filtered = requests.loc[(requests["aging_days"] >= min_aging) & (requests["headcount_gap"] >= min_gap)].copy()
    if category != "All action labels":
        filtered = filtered.loc[filtered["action_label"] == category].copy()

    average_aging = filtered["aging_days"].mean() if not filtered.empty else 0
    overdue = int(filtered["overdue"].sum()) if not filtered.empty else 0
    unsent = int(filtered["action_label"].eq("Belum Dikirim").sum()) if not filtered.empty else 0
    render_kpis([
        {"label": "Total talent requests", "value": format_count(kpis["KPI-02"])},
        {"label": "Requested headcount", "value": format_count(kpis["KPI-03"])},
        {"label": "Headcount gap", "value": format_count(kpis["KPI-10"])},
        {"label": "Average active aging", "value": format_days(average_aging)},
        {"label": "Overdue request count", "value": format_count(overdue)},
        {"label": "Unsent request count", "value": format_count(unsent)},
    ], columns_per_row=6, variant="compact")

    aging = filtered.assign(
        aging_band=pd.cut(
            filtered["aging_days"], bins=[-1, 7, 14, 30, float("inf")],
            labels=["0-7 days", "8-14 days", "15-30 days", ">30 days"],
        )
    )["aging_band"].value_counts(sort=False).rename_axis("aging_band").reset_index(name="count")
    aging = aging.loc[aging["count"].gt(0)].reset_index(drop=True)
    gaps = with_request_labels(filtered.loc[filtered["headcount_gap"].gt(0)].nlargest(10, "headcount_gap"))
    supply = with_request_labels(filtered.nlargest(10, "candidate_applications"))
    action_labels = ordered_counts(filtered["action_label"], ACTION_LABEL_ORDER)
    action_labels = action_labels.rename(columns={"category": "action_label"})

    render_section("Request workload", "The charts are sorted to surface aging, shortage, and priority concentration.")
    left, right = analytical_columns(
        "equal",
        key="request-workload-primary",
    )
    with left:
        with chart_surface(
            "Request aging distribution",
            "Requests grouped by current aging band.",
            key="request-aging-distribution",
        ):
            render_bar(
                aging,
                "aging_band",
                "count",
                "Request aging distribution",
                show_title=False,
                series_color=CHART_PRIMARY,
                x_title="Aging band",
                y_title="Requests",
                category_order=aging["aging_band"].tolist(),
                show_legend=False,
                tick_angle=-20,
            )
    with right:
        with chart_surface(
            "Largest headcount gaps",
            "Requests with the greatest remaining staffing shortfall.",
            key="request-headcount-gaps",
        ):
            render_horizontal_bar(
                gaps,
                "headcount_gap",
                REQUEST_LABEL_COLUMN,
                "Largest headcount gaps",
                show_title=False,
                x_title="Headcount gap",
                y_title="Request",
            )
    left, right = analytical_columns(
        "equal",
        key="request-workload-secondary",
    )
    with left:
        with chart_surface(
            "Candidate applications",
            "Requests ranked by candidate applications and action label.",
            key="request-candidate-supply",
        ):
            render_horizontal_bar(
                supply,
                "candidate_applications",
                REQUEST_LABEL_COLUMN,
                "Candidate applications",
                color="action_label",
                show_title=False,
                color_map=ACTION_LABEL_COLORS,
                x_title="Applications",
                y_title="Request",
                show_legend=False,
            )
    with right:
        with chart_surface(
            "Requests by action label",
            "Request volume grouped by the current operational label.",
            key="request-action-labels",
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

    render_section("Action table", "Select a request ID to preserve it for the matching page.")
    request_ids = ["Select a request", *filtered["id_talent_req"].tolist()]
    st.selectbox("Request context", request_ids, key="selected_request_id")
    columns = [
        "id_talent_req", "company_name", "nama_posisi", "request_status", "requested_headcount",
        "candidate_applications", "placements", "headcount_gap", "request_aging_days", "action_label",
    ]
    render_downloadable_table(filtered[columns], "ssdc-talent-requests.csv", "request-table")
    st.page_link("app_pages/talent_matching.py", label="Open Talent Matching", icon=":material/person_search:")


if __name__ == "__main__":
    main()
