from pathlib import Path
import re
import tomllib

from config import theme


FRONTEND = Path(
    "components/ssdc-carbon-components/"
    "ssdc_carbon_components/frontend"
)


def test_surface_tokens_define_the_carbon_layer_model() -> None:
    assert theme.SURFACE_COLORS == {
        "background": "#ffffff",
        "layer_01": "#f4f4f4",
        "layer_02": "#ffffff",
        "layer_hover": "#e8e8e8",
        "layer_selected": "#e0e0e0",
        "highlight": "#d0e2ff",
        "border_subtle": "#e0e0e0",
        "border_strong": "#c6c6c6",
        "interactive": "#0f62fe",
    }


def test_streamlit_theme_separates_canvas_surfaces_and_native_tables() -> None:
    streamlit_theme = tomllib.loads(Path(".streamlit/config.toml").read_text())["theme"]

    assert streamlit_theme["backgroundColor"] == theme.SURFACE_COLORS["layer_01"]
    assert streamlit_theme["secondaryBackgroundColor"] == theme.SURFACE_COLORS["background"]
    assert streamlit_theme["borderColor"] == theme.SURFACE_COLORS["border_strong"]
    assert streamlit_theme["dataframeBorderColor"] == theme.SURFACE_COLORS["border_subtle"]
    assert (
        streamlit_theme["dataframeHeaderBackgroundColor"]
        == theme.SURFACE_COLORS["layer_01"]
    )
    assert streamlit_theme["baseRadius"] == "none"
    assert streamlit_theme["buttonRadius"] == "none"


def test_shared_theme_uses_tokenized_canvas_and_chart_boundaries(monkeypatch) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        theme.st,
        "markdown",
        lambda body, **options: captured.update(body=body),
    )

    theme.inject_theme()

    css = str(captured["body"])
    assert "--app-surface-background: #ffffff;" in css
    assert "--app-surface-layer-01: #f4f4f4;" in css
    assert "--app-border-subtle: #e0e0e0;" in css
    assert "--app-border-strong: #c6c6c6;" in css
    assert "background: var(--app-surface-layer-01);" in css
    assert "background: var(--app-surface-background);" in css
    assert "border: 1px solid var(--app-border-subtle) !important;" in css
    assert "border-color: var(--app-border-strong) !important;" in css
    assert "border-radius: 0 !important;" in css
    assert "box-shadow: none !important;" in css


def test_carbon_surfaces_share_neutral_boundaries_and_compiled_assets() -> None:
    source = (FRONTEND / "src/index.ts").read_text()
    styles = (FRONTEND / "src/styles.css").read_text()
    built_css = (FRONTEND / "build/index-_hash_.css").read_text()

    assert "--app-surface-background: var(--st-secondary-background-color, #ffffff);" in styles
    assert "--app-surface-layer-01: var(--st-background-color, #f4f4f4);" in styles
    assert "--app-border-subtle: var(--st-border-color-light, #e0e0e0);" in styles
    assert "--app-border-strong: var(--st-border-color, #c6c6c6);" in styles
    assert ".cds-filter-toolbar" in styles
    assert ".cds-data-status" in styles
    assert ".cds-kpi-card" in styles
    assert ".cds-table-surface" in styles
    assert "border: 1px solid var(--app-border-subtle);" in styles
    assert "border-color: var(--app-border-strong);" in styles
    assert "background: transparent;" in styles
    assert "--cds-layer-accent: var(--app-surface-layer-01);" in styles
    assert 'surface.className = "cds-table-surface"' in source
    assert "surface.append(table, pagination);" in source
    assert ".cds-table-surface" in built_css
    assert "--app-border-strong:var(--st-border-color,#c6c6c6)" in built_css


def test_surface_styles_do_not_add_shadows_gradients_or_page_color_hacks() -> None:
    theme_source = Path("config/theme.py").read_text()
    component_styles = (FRONTEND / "src/styles.css").read_text()
    combined = f"{theme_source}\n{component_styles}"

    assert "linear-gradient" not in combined
    assert "radial-gradient" not in combined
    assert "nth-child" not in combined
    for value in re.findall(r"box-shadow:\s*([^;]+);", combined):
        assert value.strip() in {"none", "none !important"}

    for page in Path("app_pages").glob("*.py"):
        source = page.read_text().lower()
        assert "#ffffff" not in source
        assert "#f4f4f4" not in source
        assert "#e0e0e0" not in source
        assert "#c6c6c6" not in source
