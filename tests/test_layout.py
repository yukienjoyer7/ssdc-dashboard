from pathlib import Path

import pytest

from components import ui
from config import theme


PAGE_GRID_VARIANTS = {
    "executive_overview.py": {
        "main_supporting": 1,
        "equal": 1,
    },
    "talent_request_management.py": {
        "equal": 2,
    },
    "talent_matching.py": {
        "supporting_main": 1,
    },
    "selection_monitoring.py": {
        "equal": 1,
    },
    "placement_performance.py": {
        "equal": 2,
    },
}


def test_dashboard_layout_tokens_define_one_content_frame() -> None:
    assert theme.DASHBOARD_LAYOUT == {
        "content_max_width": "1400px",
        "sidebar_width": "16rem",
        "gutter_wide": "2rem",
        "gutter_medium": "1.5rem",
        "gutter_narrow": "1rem",
    }


def test_theme_constrains_the_main_region_responsively(monkeypatch) -> None:
    captured: dict[str, str] = {}
    monkeypatch.setattr(
        theme.st,
        "markdown",
        lambda body, **options: captured.update(body=body),
    )

    theme.inject_theme()

    css = captured["body"]
    for name, value in theme.DASHBOARD_LAYOUT.items():
        css_name = name.replace("_", "-")
        assert f"--dashboard-{css_name}: {value};" in css
    assert '[data-testid="stMain"] {' in css
    assert "padding-inline-start: var(--dashboard-sidebar-width);" in css
    assert '[data-testid="stMainBlockContainer"], .block-container {' in css
    assert "width: 100%;" in css
    assert "max-width: var(--dashboard-content-max-width);" in css
    assert "margin-inline: auto;" in css
    assert "var(--dashboard-gutter-wide)" in css
    assert "@media (max-width: 75rem)" in css
    assert '[class*="st-key-cds-analytical-grid-"]' in css
    assert "flex-direction: column;" in css
    assert "@media (max-width: 56.25rem)" in css
    assert "padding-inline: var(--dashboard-gutter-medium);" in css
    assert "@media (max-width: 48rem)" in css
    assert "padding-inline-start: 0;" in css
    assert "@media (max-width: 40rem)" in css
    assert "padding-inline: var(--dashboard-gutter-narrow);" in css
    assert "100vw" not in css
    assert "max-width: none" not in css
    assert "margin-left: -" not in css


def test_application_keeps_streamlit_wide_layout() -> None:
    source = Path("app.py").read_text()

    assert 'layout="wide"' in source
    assert 'layout="centered"' not in source


def test_analytical_columns_use_only_the_shared_grid_specs(monkeypatch) -> None:
    calls: list[tuple[tuple[int, int], str]] = []
    container_keys: list[str] = []

    def columns(spec, *, gap):
        calls.append((spec, gap))
        return [object(), object()]

    class FakeContainer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def container(*, key):
        container_keys.append(key)
        return FakeContainer()

    monkeypatch.setattr(ui.st, "container", container)
    monkeypatch.setattr(ui.st, "columns", columns)

    for variant, expected in ui.ANALYTICAL_GRID_SPECS.items():
        assert len(ui.analytical_columns(variant, key=variant)) == 2
        assert calls[-1] == (expected, "medium")
        assert container_keys[-1] == f"cds-analytical-grid-{variant}"

    with pytest.raises(ValueError, match="Unsupported analytical grid variant"):
        ui.analytical_columns("irregular", key="invalid")


def test_dashboard_pages_use_the_shared_analytical_grid() -> None:
    for filename, expected_variants in PAGE_GRID_VARIANTS.items():
        source = (Path("app_pages") / filename).read_text()

        assert "st.columns(" not in source
        for variant, count in expected_variants.items():
            assert source.count(f'"{variant}",') == count
