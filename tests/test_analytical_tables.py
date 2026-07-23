from datetime import date

import pandas as pd

from data.contracts import FilterState
from data.mock_data import build_mock_tables
from services.analytical_tables import (
    build_company_performance,
    build_request_table,
    build_selection_table,
    build_student_profile,
)
from services.analytics import resolve_outcome


def _dummy_as_of() -> pd.Timestamp:
    return pd.Timestamp("2026-03-01")


def test_student_profile_grain_is_unique_nim() -> None:
    tables = build_mock_tables()
    result = build_student_profile(tables["student_all.csv"], tables["status_student.csv"])
    assert result["NIM"].is_unique
    assert len(result) == len(tables["student_all.csv"])


def test_student_profile_columns_exist() -> None:
    tables = build_mock_tables()
    result = build_student_profile(tables["student_all.csv"], tables["status_student.csv"])
    for col in ["NIM", "nama", "program_studi", "semester", "eligible", "ketersediaan", "IPK"]:
        assert col in result.columns


def test_student_profile_no_pii_columns() -> None:
    tables = build_mock_tables()
    result = build_student_profile(tables["student_all.csv"], tables["status_student.csv"])
    for col in ["hp", "email_pribadi", "email_kampus", "email", "no_whatsapp"]:
        assert col not in result.columns


def test_request_table_derives_action_label() -> None:
    tables = build_mock_tables()
    result = build_request_table(
        tables["talent_request.csv"],
        tables["tracking_company.csv"],
        tables["tracking_student.csv"],
        _dummy_as_of(),
    )
    assert "action_label" in result.columns
    assert "headcount_gap" in result.columns
    assert result["headcount_gap"].ge(0).all()
    valid_labels = {"Belum Dikirim", "Terpenuhi", "Closed", "Belum Terpenuhi", "Kurang Kandidat"}
    assert set(result["action_label"].unique()).issubset(valid_labels)


def test_request_table_has_expected_ids() -> None:
    tables = build_mock_tables()
    result = build_request_table(
        tables["talent_request.csv"],
        tables["tracking_company.csv"],
        tables["tracking_student.csv"],
        _dummy_as_of(),
    )
    assert "id_talent_req" in result.columns
    assert "id_tracking_company" in result.columns
    assert result["id_talent_req"].notna().all()


def test_selection_table_derives_canonical_outcome_and_flags() -> None:
    tables = build_mock_tables()
    result = build_selection_table(
        tables["tracking_student.csv"],
        tables["tracking_company.csv"],
        tables["status_student.csv"],
        _dummy_as_of(),
    )
    assert "canonical_outcome" in result.columns
    assert "stale_flag" in result.columns
    assert "follow_up_overdue" in result.columns
    assert "ghosting_warning" in result.columns
    valid_outcomes = {"Placement", "Rejected", "Ghosting", "On Progress"}
    assert set(result["canonical_outcome"].unique()).issubset(valid_outcomes)


def test_selection_table_grain_is_unique_tracking_student_id() -> None:
    tables = build_mock_tables()
    result = build_selection_table(
        tables["tracking_student.csv"],
        tables["tracking_company.csv"],
        tables["status_student.csv"],
        _dummy_as_of(),
    )
    assert result["id_tracking_student"].is_unique


def test_company_performance_has_rate_columns() -> None:
    tables = build_mock_tables()
    df_request = build_request_table(
        tables["talent_request.csv"],
        tables["tracking_company.csv"],
        tables["tracking_student.csv"],
        _dummy_as_of(),
    )
    df_selection = build_selection_table(
        tables["tracking_student.csv"],
        tables["tracking_company.csv"],
        tables["status_student.csv"],
        _dummy_as_of(),
    )
    result = build_company_performance(df_request, df_selection)
    for col in ["placement_rate", "ghosting_rate", "fulfillment_rate", "total_requests"]:
        assert col in result.columns
    assert result["placement_rate"].between(0, 100).all()
    assert result["fulfillment_rate"].between(0, 100).all()


def test_company_performance_grain_is_unique_company_id() -> None:
    tables = build_mock_tables()
    df_request = build_request_table(
        tables["talent_request.csv"],
        tables["tracking_company.csv"],
        tables["tracking_student.csv"],
        _dummy_as_of(),
    )
    df_selection = build_selection_table(
        tables["tracking_student.csv"],
        tables["tracking_company.csv"],
        tables["status_student.csv"],
        _dummy_as_of(),
    )
    result = build_company_performance(df_request, df_selection)
    assert result["id_company"].is_unique


def test_resolve_outcome_maps_placement() -> None:
    result = resolve_outcome(
        pd.Series(["Finish"]),
        pd.Series(["Placement"]),
    )
    assert result.iloc[0] == "Placement"


def test_resolve_outcome_maps_rejection_prefix() -> None:
    result = resolve_outcome(
        pd.Series(["Interview User"]),
        pd.Series(["Rejection Interview User"]),
    )
    assert result.iloc[0] == "Rejected"


def test_resolve_outcome_falls_back_to_progress() -> None:
    result = resolve_outcome(
        pd.Series(["Finish"]),
        pd.Series([""]),
    )
    assert result.iloc[0] == "On Progress"


def test_resolve_outcome_rejection_on_progress_falls_back() -> None:
    result = resolve_outcome(
        pd.Series(["Interview User"]),
        pd.Series(["On Progress"]),
    )
    assert result.iloc[0] == "On Progress"


def test_request_table_no_kurang_kandidat_when_0_apps() -> None:
    """Regression: requests with 0 applications → Belum Dikirim, never Kurang Kandidat."""
    tables = build_mock_tables()
    result = build_request_table(
        tables["talent_request.csv"],
        tables["tracking_company.csv"],
        tables["tracking_student.csv"],
        _dummy_as_of(),
    )
    zero_apps = result.loc[result["candidate_applications"] == 0]
    if not zero_apps.empty:
        assert (zero_apps["action_label"] == "Belum Dikirim").all()


def test_selection_stale_flag_consistent() -> None:
    tables = build_mock_tables()
    result = build_selection_table(
        tables["tracking_student.csv"],
        tables["tracking_company.csv"],
        tables["status_student.csv"],
        _dummy_as_of(),
    )
    fresh = result.loc[~result["stale_flag"]]
    if not fresh.empty:
        assert (fresh["selection_aging_days"] <= 14).all()
