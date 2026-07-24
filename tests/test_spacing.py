from pathlib import Path

import plotly.graph_objects as go

from components import charts
from config import theme


FRONTEND = Path(
    "components/ssdc-carbon-components/"
    "ssdc_carbon_components/frontend"
)


def test_spacing_tokens_match_the_carbon_scale() -> None:
    assert theme.SPACING == {
        "01": "0.125rem",
        "02": "0.25rem",
        "03": "0.5rem",
        "04": "0.75rem",
        "05": "1rem",
        "06": "1.5rem",
        "07": "2rem",
        "08": "2.5rem",
        "09": "3rem",
    }
    assert {
        token: theme.spacing_px(token)
        for token in theme.SPACING
    } == {
        "01": 2,
        "02": 4,
        "03": 8,
        "04": 12,
        "05": 16,
        "06": 24,
        "07": 32,
        "08": 40,
        "09": 48,
    }


def test_shared_theme_uses_spacing_tokens_without_stacked_header_margins(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        theme.st,
        "markdown",
        lambda body, **options: captured.update(body=body),
    )

    theme.inject_theme()

    css = str(captured["body"])
    for token, value in theme.SPACING.items():
        assert f"--cds-spacing-{token}: {value};" in css
    assert "padding: calc(3rem + var(--cds-spacing-06))" in css
    assert "var(--dashboard-gutter-wide)" in css
    assert "var(--cds-spacing-09);" in css
    assert '.cds-page-header {\n            max-width: 52rem;\n            margin: 0;' in css
    assert '.cds-section-header {\n            max-width: 56rem;\n            margin: 0;' in css
    assert "margin-block-end: var(--cds-spacing-03);" in css
    assert "padding: var(--cds-spacing-05);" in css
    assert "margin: 0 0 var(--cds-spacing-04);" in css
    assert "padding: 5.5rem" not in css
    assert "margin: 2rem 0 0.75rem" not in css


def test_carbon_components_bridge_to_shared_spacing_tokens() -> None:
    styles = (FRONTEND / "src/styles.css").read_text()
    built_css = (FRONTEND / "build/index-_hash_.css").read_text()

    for token, value in theme.SPACING.items():
        assert (
            f"--app-spacing-{token}: var(--cds-spacing-{token}, {value});"
            in styles
        )
    assert ".cds-filter-container {\n  min-width: 0;\n  margin-block-end: 0;" in styles
    assert "padding: var(--app-spacing-04) var(--app-spacing-05);" in styles
    assert "margin-block-end: var(--app-spacing-03);" in styles
    assert (
        ".cds-kpi-section--default,\n"
        ".cds-kpi-section--compact {\n"
        "  margin-block-end: var(--app-spacing-05);"
    ) in styles
    assert (
        ".cds-kpi-section--primary {\n"
        "  margin-block-end: var(--app-spacing-03);"
    ) in styles
    assert "margin-block-end: 1.5rem;" not in styles
    assert "--app-spacing-09:var(--cds-spacing-09,3rem)" in built_css


def test_plotly_outer_margin_uses_the_shared_spacing_scale() -> None:
    figure = charts._base_layout(go.Figure())

    assert figure.layout.margin.l == 8
    assert figure.layout.margin.r == 8
    assert figure.layout.margin.t == 48
    assert figure.layout.margin.b == 8


def test_application_has_no_manual_empty_spacing_hacks() -> None:
    files = [
        Path("app.py"),
        *Path("app_pages").glob("*.py"),
        *(
            path
            for path in Path("components").glob("*.py")
            if path.name != "example.py"
        ),
    ]
    forbidden = (
        'st.write("")',
        "st.write('')",
        'st.markdown("")',
        "st.markdown('')",
        "st.empty()",
        "<br>",
        "<br/>",
        "<br />",
    )

    for path in files:
        source = path.read_text()
        for pattern in forbidden:
            assert pattern not in source, f"{path} contains spacing hack {pattern}"
