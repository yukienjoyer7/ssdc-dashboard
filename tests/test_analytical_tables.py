from datetime import date

import pandas as pd

from data.contracts import FilterState
from data.mock_data import build_mock_tables
from services.analytical_tables import (
    _build_dimensional_performance,
    build_company_performance,
    build_placement_type_performance,
    build_program_performance,
    build_request_table,
    build_sector_performance,
    build_selection_table,
    build_student_profile,
    build_work_arrangement_performance,
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


def _build_test_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
    df_company = tables["company.csv"]
    return df_selection, df_request, df_company


_RATE_COLUMNS = [
    "total_applications", "unique_candidates", "placements",
    "ghosting", "rejected", "requested_headcount",
    "placement_rate", "ghosting_rate", "rejection_rate", "fulfillment_rate",
]


def test_program_performance_grain_is_unique() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_program_performance(df_selection, df_request)
    assert result["study_program"].is_unique


def test_program_performance_has_expected_columns() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_program_performance(df_selection, df_request)
    for col in _RATE_COLUMNS:
        assert col in result.columns


def test_program_performance_rates_in_range() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_program_performance(df_selection, df_request)
    for col in ["placement_rate", "ghosting_rate", "rejection_rate", "fulfillment_rate"]:
        assert result[col].between(0, 100).all()


def test_placement_type_performance_grain_is_unique() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_placement_type_performance(df_selection, df_request)
    assert result["placement_type"].is_unique


def test_placement_type_performance_has_expected_columns() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_placement_type_performance(df_selection, df_request)
    for col in _RATE_COLUMNS:
        assert col in result.columns


def test_placement_type_performance_rates_in_range() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_placement_type_performance(df_selection, df_request)
    for col in ["placement_rate", "ghosting_rate", "rejection_rate", "fulfillment_rate"]:
        assert result[col].between(0, 100).all()


def test_sector_performance_grain_is_unique() -> None:
    df_selection, df_request, df_company = _build_test_tables()
    result = build_sector_performance(df_selection, df_request, df_company)
    assert result["industry_sector"].is_unique


def test_sector_performance_has_expected_columns() -> None:
    df_selection, df_request, df_company = _build_test_tables()
    result = build_sector_performance(df_selection, df_request, df_company)
    for col in _RATE_COLUMNS:
        assert col in result.columns


def test_sector_performance_rates_in_range() -> None:
    df_selection, df_request, df_company = _build_test_tables()
    result = build_sector_performance(df_selection, df_request, df_company)
    for col in ["placement_rate", "ghosting_rate", "rejection_rate", "fulfillment_rate"]:
        assert result[col].between(0, 100).all()


def test_work_arrangement_performance_grain_is_unique() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_work_arrangement_performance(df_selection, df_request)
    assert result["working_arrangement"].is_unique


def test_work_arrangement_performance_has_expected_columns() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_work_arrangement_performance(df_selection, df_request)
    for col in _RATE_COLUMNS:
        assert col in result.columns


def test_work_arrangement_performance_rates_in_range() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_work_arrangement_performance(df_selection, df_request)
    for col in ["placement_rate", "ghosting_rate", "rejection_rate", "fulfillment_rate"]:
        assert result[col].between(0, 100).all()


def test_dimensional_performance_placement_rate_formula() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_program_performance(df_selection, df_request)
    expected = (result["placements"] / result["total_applications"].replace(0, pd.NA) * 100).fillna(0).round(1)
    pd.testing.assert_series_equal(result["placement_rate"], expected, check_names=False)


def test_dimensional_performance_ghosting_rate_formula() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_placement_type_performance(df_selection, df_request)
    expected = (result["ghosting"] / result["total_applications"].replace(0, pd.NA) * 100).fillna(0).round(1)
    pd.testing.assert_series_equal(result["ghosting_rate"], expected, check_names=False)


def test_dimensional_performance_rejection_rate_formula() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_program_performance(df_selection, df_request)
    expected = (result["rejected"] / result["total_applications"].replace(0, pd.NA) * 100).fillna(0).round(1)
    pd.testing.assert_series_equal(result["rejection_rate"], expected, check_names=False)


def test_dimensional_performance_no_negative_rates() -> None:
    df_selection, df_request, _ = _build_test_tables()
    for builder in [
        lambda: build_program_performance(df_selection, df_request),
        lambda: build_placement_type_performance(df_selection, df_request),
        lambda: build_work_arrangement_performance(df_selection, df_request),
    ]:
        result = builder()
        for col in ["placement_rate", "ghosting_rate", "rejection_rate", "fulfillment_rate"]:
            assert (result[col] >= 0).all()


def test_dimensional_performance_empty_selection() -> None:
    empty = pd.DataFrame()
    result = _build_dimensional_performance(empty, pd.DataFrame(), "study_program")
    assert result.empty


def test_dimensional_performance_missing_dimension_column() -> None:
    df = pd.DataFrame({"NIM": ["001"], "canonical_outcome": ["Placement"], "id_talent_req": ["TR001"]})
    result = _build_dimensional_performance(df, pd.DataFrame(), "nonexistent_col")
    assert result.empty


def test_dimensional_performance_unknown_dimension_fallback() -> None:
    df_selection, df_request, _ = _build_test_tables()
    df_selection = df_selection.copy()
    df_selection.loc[0, "study_program"] = pd.NA
    result = build_program_performance(df_selection, df_request)
    assert "Unknown" in result["study_program"].values


def test_sector_performance_missing_company_returns_empty() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_sector_performance(df_selection, df_request, pd.DataFrame())
    assert result.empty


def test_sector_performance_missing_id_company_returns_empty() -> None:
    df_selection, df_request, _ = _build_test_tables()
    bad_company = pd.DataFrame({"industry_sector": ["Tech"]})
    result = build_sector_performance(df_selection, df_request, bad_company)
    assert result.empty


def test_work_arrangement_performance_missing_request_returns_empty() -> None:
    df_selection, _, _ = _build_test_tables()
    result = build_work_arrangement_performance(df_selection, pd.DataFrame())
    assert result.empty


def test_work_arrangement_performance_missing_working_arrangement_returns_empty() -> None:
    df_selection, df_request, _ = _build_test_tables()
    bad_request = df_request[["id_talent_req"]].copy()
    result = build_work_arrangement_performance(df_selection, bad_request)
    assert result.empty


def test_dimensional_performance_unique_candidates_leq_applications() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_program_performance(df_selection, df_request)
    assert (result["unique_candidates"] <= result["total_applications"]).all()


def test_dimensional_performance_outcomes_sum_leq_applications() -> None:
    df_selection, df_request, _ = _build_test_tables()
    result = build_placement_type_performance(df_selection, df_request)
    outcome_sum = result["placements"] + result["ghosting"] + result["rejected"]
    assert (outcome_sum <= result["total_applications"]).all()

