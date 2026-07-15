from datetime import date

from data.contracts import FilterState
from data.loaders import DashboardData
from data.mock_data import build_mock_tables
from services.analytics import matching_table, placement_table, request_table, selection_table


def _mock_dashboard() -> DashboardData:
    return DashboardData(build_mock_tables(), "test preview", True)


def test_request_service_derives_action_fields() -> None:
    result = request_table(_mock_dashboard(), FilterState(date_start=date(2026, 1, 1), date_end=date(2026, 3, 1)))

    assert len(result) == 6
    assert {"headcount_gap", "aging_days", "priority_category", "priority_reason"}.issubset(result.columns)
    assert result["headcount_gap"].ge(0).all()


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
