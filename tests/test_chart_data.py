import pandas as pd

from components.chart_data import monthly_counts, ordered_counts, with_request_labels


def test_request_chart_labels_include_unique_request_ids() -> None:
    frame = pd.DataFrame(
        {
            "company_name": ["Northstar Labs", "Northstar Labs"],
            "nama_posisi": ["Data Analyst", "Data Analyst"],
            "id_talent_req": ["TR001", "TR002"],
        }
    )

    result = with_request_labels(frame)

    assert result["chart_label"].tolist() == [
        "Northstar Labs / Data Analyst · TR001",
        "Northstar Labs / Data Analyst · TR002",
    ]


def test_ordered_counts_keeps_observed_categories_in_business_order() -> None:
    result = ordered_counts(
        pd.Series(["Closed", "Kurang Kandidat", "Closed"]),
        ["Kurang Kandidat", "Closed", "Belum Terpenuhi"],
    )

    assert result.to_dict("records") == [
        {"category": "Kurang Kandidat", "count": 1},
        {"category": "Closed", "count": 2},
    ]


def test_monthly_counts_zero_fills_a_shared_chronological_domain() -> None:
    requests = pd.DataFrame({"request_date": ["2026-01-08", "2026-03-08"]})
    placements = pd.DataFrame({"placement_date": ["2026-02-26"]})

    result = monthly_counts(
        {
            "Talent requests": (requests, "request_date"),
            "Placements": (placements, "placement_date"),
        },
        "count",
    )

    assert result.to_dict("records") == [
        {"month": "2026-01", "count": 1, "metric": "Talent requests"},
        {"month": "2026-02", "count": 0, "metric": "Talent requests"},
        {"month": "2026-03", "count": 1, "metric": "Talent requests"},
        {"month": "2026-01", "count": 0, "metric": "Placements"},
        {"month": "2026-02", "count": 1, "metric": "Placements"},
        {"month": "2026-03", "count": 0, "metric": "Placements"},
    ]
