import ast
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
    render_feedback,
    render_shell,
)
from components.ui import render_data_status, render_kpis
from data.contracts import FilterState
from data.loaders import DashboardData
from data.mock_data import build_mock_tables


def _mock_dashboard() -> DashboardData:
    return DashboardData(build_mock_tables(), "test preview", True)


def test_carbon_page_registry_is_complete_and_resolves_navigation_targets() -> None:
    assert len(PAGE_SPECS) == 5
    assert [page.title for page in PAGE_SPECS] == [
        "Ringkasan Eksekutif",
        "Manajemen Permintaan Talenta",
        "Pencocokan Talenta",
        "Pemantauan Seleksi",
        "Kinerja Penempatan",
    ]
    assert page_spec_for_slug("talent-matching").title == "Pencocokan Talenta"
    assert page_spec_for_title("Kinerja Penempatan").slug == "placement-performance"
    assert page_spec_for_slug("missing") is None


def test_page_registry_uses_carbon_navigation_icons_and_pictograms() -> None:
    assert [(page.carbon_icon, page.pictogram) for page in PAGE_SPECS] == [
        ("dashboard", "global--analytics"),
        ("task", "list--checkbox"),
        ("search", "user--search"),
        ("warning--alt", "chart--stepper"),
        ("chart--line", "user--analytics"),
    ]
    assert page_spec_for_title("Executive Overview").pictogram == "global--analytics"


def test_shell_preserves_page_registry_and_active_route(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def capture(view, data, *, key):
        captured.update({"view": view, "data": data, "key": key})
        return None

    monkeypatch.setattr("components.carbon_ui._render_surface", capture)
    render_shell("talent-matching", key="test-shell")

    assert captured["view"] == "shell"
    assert captured["key"] == "test-shell"
    assert captured["data"]["active_page"] == "talent-matching"
    assert captured["data"]["context_label"] == "Data prototipe"
    assert [page["slug"] for page in captured["data"]["pages"]] == [
        page.slug for page in PAGE_SPECS
    ]
    assert [page["pictogram"] for page in captured["data"]["pages"]] == [
        page.pictogram for page in PAGE_SPECS
    ]


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


def test_data_status_preserves_technical_details_behind_disclosure(monkeypatch) -> None:
    captured: dict[str, object] = {}
    data = DashboardData(
        build_mock_tables(),
        "/private/data_clean",
        False,
        ("Review the source contract.",),
    )

    monkeypatch.setattr(
        "components.ui.render_data_status_surface",
        lambda **payload: captured.update(payload),
    )
    render_data_status(
        data,
        "Canonical KPI preview; dataset as-of date: {as_of_date}.",
        key="test-data-status",
    )

    details = {
        item["label"]: item["value"]
        for item in captured["detail_items"]
    }
    assert captured["mode"] == "local"
    assert captured["record_count"] == sum(len(frame) for frame in data.tables.values())
    assert captured["kpi_status"] == "provisional"
    assert captured["warnings"] == ["Review the source contract."]
    assert "source" not in captured
    assert details["Sumber"] == "/private/data_clean"
    assert details["Catatan"] == f"{captured['record_count']:,}"
    assert details["Data per"] == captured["as_of_date"]
    assert "Menunggu validasi PM/Engineer Data." in details["Catatan validasi"]


def test_data_status_identifies_mock_data(monkeypatch) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        "components.ui.render_data_status_surface",
        lambda **payload: captured.update(payload),
    )

    data = _mock_dashboard()
    render_data_status(
        data,
        "Eligibility rules are provisional.",
        key="test-prototype-status",
    )

    assert captured["mode"] == "prototype"
    assert captured["record_count"] == sum(len(frame) for frame in data.tables.values())
    assert captured["as_of_date"]


def test_error_feedback_remains_a_prominent_notification(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def capture(view, data, *, key):
        captured.update({"view": view, "data": data, "key": key})

    monkeypatch.setattr("components.carbon_ui._render_surface", capture)
    render_feedback(
        "Dataset failed to load",
        "Required source tables are unavailable.",
        kind="error",
        key="load-error",
    )

    assert captured["view"] == "feedback"
    assert captured["data"]["kind"] == "error"


def test_kpi_variants_are_forwarded_through_the_shared_renderer(monkeypatch) -> None:
    captured: dict[str, object] = {}
    items = [{"label": "Placements", "value": "7,534"}]
    monkeypatch.setattr(
        "components.ui.render_kpi_row",
        lambda forwarded, **options: captured.update(
            {"items": forwarded, **options},
        ),
    )

    render_kpis(
        items,
        columns_per_row=4,
        variant="primary",
        section_label="Primary outcomes",
        key="primary-outcomes",
    )

    assert captured["items"] == items
    assert captured["columns_per_row"] == 4
    assert captured["variant"] == "primary"
    assert captured["section_label"] == "Primary outcomes"


def test_executive_overview_uses_the_required_kpi_groups() -> None:
    tree = ast.parse(Path("app_pages/executive_overview.py").read_text())
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "render_kpis"
    ]

    groups = [
        [item.values[0].value for item in call.args[0].elts]
        for call in calls
    ]
    options = [
        {
            keyword.arg: keyword.value.value
            for keyword in call.keywords
            if isinstance(keyword.value, ast.Constant)
        }
        for call in calls
    ]

    assert groups == [
        ["Kebutuhan talenta", "Penempatan", "Tingkat penempatan", "Tingkat ghosting"],
        ["Total perusahaan", "Total permintaan talenta", "Lamaran kandidat", "Kandidat unik"],
    ]
    assert options[0]["variant"] == "primary"
    assert options[0]["section_label"] == "Hasil utama"
    assert options[1]["variant"] == "secondary"
    assert options[1]["section_label"] == "Volume proses"


def test_kpi_variants_match_page_hierarchy() -> None:
    expected_variants = {
        "talent_request_management.py": ["compact"],
        "talent_matching.py": ["default", "compact"],
        "selection_monitoring.py": ["compact"],
    }
    for page in Path("app_pages").glob("*.py"):
        if page.name == "executive_overview.py":
            continue
        tree = ast.parse(page.read_text())
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "render_kpis"
        ]
        variants = [
            next(
                (keyword.value.value for keyword in call.keywords if keyword.arg == "variant"),
                "default",
            )
            for call in calls
        ]
        assert variants == expected_variants.get(page.name, ["default"] * len(calls))


def test_compiled_carbon_assets_and_accessibility_hooks_exist() -> None:
    frontend = Path("components/ssdc-carbon-components/ssdc_carbon_components/frontend")
    build = frontend / "build"
    source = (frontend / "src/index.ts").read_text()
    styles = (frontend / "src/styles.css").read_text()
    compiled_js = "\n".join(path.read_text() for path in build.glob("index-*.js"))
    compiled_css = "\n".join(path.read_text() for path in build.glob("index-*.css"))
    assert compiled_js
    assert compiled_css
    assert 'setAttribute("aria-label", "Navigasi dasbor")' in source
    assert 'button-label-inactive' in source
    assert 'menu.setAttribute("collapse-mode", "rail")' in source
    assert 'className = "cds-header__global"' in source
    assert 'help.dataset.testid = "help-placeholder"' in source
    assert 'Bantuan segera hadir' in source
    assert 'sideNav.setAttribute("collapse-mode", "fixed")' in source
    assert 'data-ssdc-sidebar-collapsed' in source
    assert 'className = "cds-sidebar__brand"' in source
    assert 'import GlobalAnalytics from "@carbon/pictograms/svg/global--analytics.svg?raw"' in source
    assert 'import Dashboard16 from "@carbon/icons/es/dashboard/16.js"' in source
    assert 'iconNode.setAttribute("slot", "title-icon")' in source
    assert 'case "pictogram"' in source
    assert 'productDescription.textContent = "Dasbor Intelijen Talenta"' in source
    assert 'link.setAttribute("aria-current", "page")' in source
    assert 'header.setAttribute("aria-label", "Header dasbor")' in source
    assert 'header.append(menu, global)' in source
    assert 'link.setAttribute("aria-label", page.title)' in source
    assert 'new MutationObserver(syncGlobalLayout)' in source
    assert 'manualRailStyle.textContent' in source
    assert 'inline-size: 3rem' in source
    assert 'headerBrand.textContent = "SSDC"' not in source
    assert 'product.textContent = "Talent Intelligence"' not in source
    assert 'className = "cds-filter-toolbar"' in source
    assert 'className = "cds-filter-toolbar__summary"' in source
    assert 'toggle.setAttribute("kind", "primary")' in source
    assert 'case "data_status"' in source
    assert 'className = "cds-data-status__summary"' in source
    assert 'detailsToggle.setAttribute("aria-expanded", "false")' in source
    assert "detailsPanel.hidden = true" in source
    assert 'notification.setAttribute("kind", data.kind ?? "info")' in source
    assert 'className = "cds-kpi-section__title"' in source
    assert "cds-kpi-grid--${variant}" in source
    assert "cds-kpi-card--${variant}" in source
    assert 'type: "apply_filters"' in source
    assert 'cds-pagination-changed-current' in source
    assert 'type: "table_page"' in source
    assert "min-block-size: 4rem" in styles
    assert ".cds-filter-toolbar__actions" in styles
    assert "min-block-size: 2.5rem" in styles
    assert "padding: var(--app-spacing-01) var(--app-spacing-03)" in styles
    assert "gap: var(--app-spacing-03);\n    padding: var(--app-spacing-03) var(--app-spacing-04);" in styles
    assert "gap: var(--app-spacing-01);\n    min-block-size: 2.5rem;" in styles
    assert "@media (max-width: 40rem)" in styles
    assert "flex-direction: row;" in styles
    assert ".cds-data-status__details[hidden]" in styles
    assert ".cds-kpi-grid--primary" in styles
    assert ".cds-kpi-grid--compact" in styles
    assert ".cds-kpi-grid--default" in styles
    assert "repeat(var(--cds-kpi-columns, 4), minmax(0, 1fr))" in styles
    assert "--cds-background-selected: var(--cds-highlight)" in styles
    assert "--cds-border-interactive: var(--cds-interactive-01)" in styles
    assert ".cds-nav-item:not(.cds-nav-item--active)::part(link):hover" in styles
    assert ".cds-nav-item--active::part(link)" in styles
    assert ".cds-nav-item::part(link):focus-visible" in styles
    assert "outline: 2px solid var(--app-focus-color)" in styles
    assert "border-inline-end: 1px solid var(--cds-sidebar-border)" in styles
    assert "--cds-background: var(--cds-sidebar-background)" in styles
    assert "background: var(--cds-sidebar-background)" in styles
    assert ".cds-header-product" not in styles
    assert ".cds-header-context" in styles
    assert "background: var(--app-surface-background)" in styles
    assert "border-block-end: 1px solid var(--app-border-subtle)" in styles
    assert "cds-side-nav:not([expanded])" in styles
    assert "justify-content: center" in styles
    assert "display: none" in styles
    assert ".cds-page-pictogram" in styles
    assert "min-block-size: 2.75rem" in styles
    assert "Dasbor Intelijen Talenta" in compiled_js
    assert ".cds-sidebar__brand" in compiled_css
    assert "@media (max-width: 64rem)" in styles
    assert "@media (max-width: 40rem)" in styles
    assert "nth-child" not in styles
    assert "!important" not in styles
    assert "cds-inline-notification {\n  display: block;\n}" not in styles
