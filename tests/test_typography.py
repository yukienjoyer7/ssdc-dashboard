from pathlib import Path
import tomllib

import plotly.graph_objects as go

from components import charts, ui
from config import theme


FRONTEND = Path(
    "components/ssdc-carbon-components/"
    "ssdc_carbon_components/frontend"
)


def test_typography_tokens_use_the_productive_carbon_scale() -> None:
    assert theme.FONT_FAMILY == "'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif"
    assert theme.TYPE_SCALE == {
        "page_title": "2rem",
        "section_title": "1.125rem",
        "subsection_title": "1rem",
        "body": "1rem",
        "page_description": "0.9375rem",
        "body_compact": "0.875rem",
        "label": "0.8125rem",
        "helper": "0.75rem",
        "kpi_primary": "2rem",
        "kpi_compact": "1.5rem",
        "chart_title": "1rem",
    }
    assert theme.TYPE_WEIGHTS == {
        "regular": 400,
        "medium": 500,
        "semibold": 600,
    }
    assert theme.PLOTLY_FONT_SIZES == {
        "body": 13,
        "axis": 12,
        "legend": 12,
        "tooltip": 13,
    }


def test_streamlit_theme_uses_ibm_plex_at_a_readable_root_size() -> None:
    streamlit_theme = tomllib.loads(Path(".streamlit/config.toml").read_text())["theme"]

    assert streamlit_theme["baseFontSize"] == 16
    assert streamlit_theme["baseFontWeight"] == 400
    assert "IBM Plex Sans" in streamlit_theme["font"]
    assert "wght@400;500;600&" in streamlit_theme["font"]
    assert "700" not in streamlit_theme["font"]
    assert streamlit_theme["headingFont"] == streamlit_theme["font"]
    assert streamlit_theme["headingFontSizes"] == [
        "2rem",
        "1.25rem",
        "1.125rem",
        "1rem",
        "0.875rem",
        "0.75rem",
    ]
    assert streamlit_theme["headingFontWeights"] == [600, 600, 600, 500, 500, 500]


def test_shared_theme_emits_semantic_typography_classes(monkeypatch) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        theme.st,
        "markdown",
        lambda body, **options: captured.update(body=body, options=options),
    )

    theme.inject_theme()

    css = str(captured["body"])
    assert "--app-font-family: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;" in css
    assert "--app-type-page-title: 2rem;" in css
    assert "--app-type-helper: 0.75rem;" in css
    assert ".cds-page-title" in css
    assert "font-size: clamp(1.75rem, 2vw, var(--app-type-page-title));" in css
    assert ".cds-page-description" in css
    assert ".cds-section-heading" in css
    assert ".cds-section-note" in css
    assert "carbon-page-header" not in css
    assert captured["options"] == {"unsafe_allow_html": True}


def test_page_and_section_headers_are_semantic_and_escape_copy(monkeypatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    monkeypatch.setattr(
        ui.st,
        "markdown",
        lambda body, **options: calls.append((body, options)),
    )

    ui.render_page_header("01 / Command <view>", "Executive & Overview", "Demand > supply")
    ui.render_section("Pipeline <movement>", "Requests & placements")

    page_markup, page_options = calls[0]
    assert '<header class="cds-page-header">' in page_markup
    assert '<p class="cds-kicker">01 / Command &lt;view&gt;</p>' in page_markup
    assert '<h1 class="cds-page-title">Executive &amp; Overview</h1>' in page_markup
    assert '<p class="cds-page-description">Demand &gt; supply</p>' in page_markup
    assert page_options == {"unsafe_allow_html": True}

    section_markup, section_options = calls[1]
    assert '<header class="cds-section-header">' in section_markup
    assert '<h2 class="cds-section-heading">Pipeline &lt;movement&gt;</h2>' in section_markup
    assert '<p class="cds-section-note">Requests &amp; placements</p>' in section_markup
    assert section_options == {"unsafe_allow_html": True}


def test_plotly_uses_shared_font_sizes_and_text_colors() -> None:
    figure = charts._base_layout(go.Figure())

    assert figure.layout.font.family == theme.FONT_FAMILY
    assert figure.layout.font.size == 13
    assert figure.layout.font.color == theme.TEXT_COLORS["primary"]
    assert figure.layout.xaxis.tickfont.size == 12
    assert figure.layout.xaxis.tickfont.color == theme.TEXT_COLORS["secondary"]
    assert figure.layout.yaxis.tickfont.size == 12
    assert figure.layout.yaxis.tickfont.color == theme.TEXT_COLORS["secondary"]
    assert figure.layout.legend.font.size == 12
    assert figure.layout.legend.font.color == theme.TEXT_COLORS["secondary"]
    assert figure.layout.hoverlabel.font.size == 13


def test_carbon_component_typography_is_shared_and_compiled() -> None:
    source = (FRONTEND / "src/index.ts").read_text()
    styles = (FRONTEND / "src/styles.css").read_text()
    built_css = (FRONTEND / "build/index-_hash_.css").read_text()

    assert "--app-type-section-title: 1.125rem;" in styles
    assert "--app-type-body-compact: 0.875rem;" in styles
    assert "--app-type-label: 0.8125rem;" in styles
    assert "--app-type-helper: 0.75rem;" in styles
    assert ".cds-nav-item--active" in styles
    assert "font-size: clamp(1.75rem, 2vw, var(--app-type-kpi-primary));" in styles
    assert "font-size: var(--app-type-kpi-compact);" in styles
    assert "font-variant-numeric: tabular-nums;" in styles
    assert "cds-table-header-cell" in styles
    assert 'link.className = `cds-nav-item${isActive ? " cds-nav-item--active" : ""}`;' in source
    assert 'document.createElement("h2")' in source
    assert ".cds-nav-item--active" in built_css
    assert "--app-type-kpi-primary:2rem" in built_css
