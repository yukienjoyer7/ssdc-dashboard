from datetime import date
from pathlib import Path

import pandas as pd

from components.carbon_ui import (
    PAGE_SPECS,
    _filter_state,
    _json_safe,
    _table_rows,
    default_filters,
    page_spec_for_slug,
    page_spec_for_title,
)
from data.contracts import FilterState
from data.loaders import DashboardData
from data.mock_data import build_mock_tables


def _mock_dashboard() -> DashboardData:
    return DashboardData(build_mock_tables(), "test preview", True)


def test_carbon_page_registry_is_complete_and_resolves_navigation_targets() -> None:
    assert len(PAGE_SPECS) == 5
    assert page_spec_for_slug("talent-matching").title == "Talent matching"
    assert page_spec_for_title("Placement performance").slug == "placement-performance"
    assert page_spec_for_slug("missing") is None


def test_default_filters_use_the_available_dataset_bounds() -> None:
    filters = default_filters(_mock_dashboard())

    assert filters.date_start is not None
    assert filters.date_end is not None
    assert filters.company == "All companies"
    assert filters.placement_type == "All placement types"


def test_filter_actions_preserve_unrelated_values_and_parse_dates() -> None:
    fallback = FilterState(
        date_start=date(2026, 1, 1),
        date_end=date(2026, 3, 31),
        company="Acme",
        study_program="All study programs",
    )

    result = _filter_state(
        {"date_start": "2026-02-01", "date_end": "2026-02-28", "company": "Globex"},
        fallback,
    )

    assert result.date_start == date(2026, 2, 1)
    assert result.date_end == date(2026, 2, 28)
    assert result.company == "Globex"
    assert result.study_program == "All study programs"


def test_table_values_are_json_safe_for_component_transport() -> None:
    assert _json_safe(date(2026, 7, 22)) == "2026-07-22"
    assert _json_safe(float("nan")) is None
    assert _json_safe(42) == 42


def test_table_rows_are_sliced_before_component_transport() -> None:
    frame = pd.DataFrame({"id": range(120), "label": [f"Row {value}" for value in range(120)]})

    rows = _table_rows(frame.iloc[50:100], ["id", "label"])

    assert len(rows) == 50
    assert rows[0] == {"id": 50, "label": "Row 50"}
    assert rows[-1]["id"] == 99


def test_compiled_carbon_assets_and_accessibility_hooks_exist() -> None:
    frontend = Path("components/ssdc-carbon-components/ssdc_carbon_components/frontend")
    build = frontend / "build"
    source = (frontend / "src/index.ts").read_text()
    assert list(build.glob("index-*.js"))
    assert list(build.glob("index-*.css"))
    assert 'setAttribute("aria-label", "Dashboard navigation")' in source
    assert 'button-label-inactive' in source
    assert 'type: "apply_filters"' in source
    assert 'cds-pagination-changed-current' in source
    assert 'type: "table_page"' in source
