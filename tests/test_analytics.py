from datetime import date

import pandas as pd

from data.contracts import FilterState
from data.loaders import DashboardData
from data.mock_data import build_mock_tables
from services.analytics import (
    canonical_kpis,
    dataset_as_of_date,
    matching_table,
    placement_table,
    request_table,
    selection_table,
    semantic_matching_table,
)


def _mock_dashboard() -> DashboardData:
    return DashboardData(build_mock_tables(), "test preview", True)


def _mock_scores() -> pd.DataFrame:
    return pd.DataFrame({
        "id_talent_req": ["TR001", "TR001", "TR001"],
        "NIM": ["2026001", "2026002", "2026003"],
        "semantic_score": [0.85, 0.72, 0.61],
        "semantic_rank": [1, 2, 3],
        "minimum_semester": [3, 3, 3],
    })


def test_request_service_derives_action_fields() -> None:
    result = request_table(_mock_dashboard(), FilterState(date_start=date(2026, 1, 1), date_end=date(2026, 3, 1)))

    assert len(result) == 6
    assert {"headcount_gap", "request_aging_days", "action_label", "placements"}.issubset(result.columns)
    assert result["headcount_gap"].ge(0).all()
    assert "priority_score" not in result.columns


def test_canonical_kpis_use_canonical_denominators_and_as_of_date() -> None:
    dashboard = _mock_dashboard()
    kpis = canonical_kpis(dashboard, FilterState())
    selection = selection_table(dashboard, FilterState())
    requests = request_table(dashboard, FilterState())

    assert kpis["KPI-04"] == len(selection)
    assert kpis["KPI-05"] == selection["NIM"].nunique()
    assert kpis["KPI-06"] == int(selection["canonical_outcome"].eq("Placement").sum())
    assert kpis["KPI-07"] == kpis["KPI-06"] / kpis["KPI-04"] * 100
    assert kpis["KPI-09"] == kpis["KPI-06"] / requests["requested_headcount"].sum() * 100
    assert kpis["as_of_date"] == dataset_as_of_date(dashboard).date().isoformat()


def test_matching_service_returns_explanations_and_eligibility() -> None:
    result, request = matching_table(_mock_dashboard(), "TR001", FilterState())

    assert request is not None
    assert not result.empty
    assert {"match_score", "eligible", "explanation", "recommendation"}.issubset(result.columns)
    assert result["explanation"].str.len().gt(0).all()


def test_selection_and_placement_services_expose_monitoring_flags() -> None:
    selection = selection_table(_mock_dashboard(), FilterState())
    placements = placement_table(_mock_dashboard(), FilterState())

    assert {"follow_up_overdue", "ghosting_warning", "stage_aging_days"}.issubset(selection.columns)
    assert not placements.empty
    assert placements["progress_student"].eq("Placement").all()


def test_semantic_matching_returns_none_for_missing_request() -> None:
    result, request = semantic_matching_table(_mock_dashboard(), "TR999", FilterState())
    assert result.empty
    assert request is None


def test_semantic_matching_returns_request_when_scores_missing(monkeypatch) -> None:
    monkeypatch.setattr("services.analytics._load_semantic_scores", lambda: None)
    result, request = semantic_matching_table(_mock_dashboard(), "TR001", FilterState())
    assert result.empty
    assert request is not None
    assert request["id_talent_req"] == "TR001"


def test_semantic_matching_returns_ranked_results(monkeypatch) -> None:
    monkeypatch.setattr("services.analytics._load_semantic_scores", lambda: _mock_scores())
    result, request = semantic_matching_table(_mock_dashboard(), "TR001", FilterState())
    assert request is not None
    assert len(result) == 3
    assert result.iloc[0]["semantic_score"] == 0.85
    assert result.iloc[2]["semantic_score"] == 0.61
    assert {"semantic_score", "semantic_rank", "eligible", "explanation", "recommendation"}.issubset(result.columns)


def test_semantic_matching_computes_eligibility(monkeypatch) -> None:
    monkeypatch.setattr("services.analytics._load_semantic_scores", lambda: _mock_scores())
    result, _ = semantic_matching_table(_mock_dashboard(), "TR001", FilterState())
    assert "eligible" in result.columns
    assert "meets_semester" in result.columns
    assert result["explanation"].str.contains("Relevance").all()


def test_semantic_matching_respects_study_program_filter(monkeypatch) -> None:
    monkeypatch.setattr("services.analytics._load_semantic_scores", lambda: _mock_scores())
    filters = FilterState(study_program="Statistika")
    result, _ = semantic_matching_table(_mock_dashboard(), "TR001", filters)
    assert all(program == "Statistika" for program in result["program_studi"])
