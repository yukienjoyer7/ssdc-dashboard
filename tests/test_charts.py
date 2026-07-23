from pathlib import Path

import pandas as pd

from components import charts


def test_chart_surface_uses_a_scoped_bordered_container(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeContainer:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def container(**options):
        captured["container"] = options
        return FakeContainer()

    def markdown(body, **options):
        captured["markup"] = body
        captured["markup_options"] = options

    monkeypatch.setattr(charts.st, "container", container)
    monkeypatch.setattr(charts.st, "markdown", markdown)

    with charts.chart_surface(
        "Requests < placements",
        "Monthly requests & completed placements.",
        key="request-trend",
    ):
        captured["body_rendered"] = True

    assert captured["container"] == {
        "border": True,
        "key": "cds-chart-surface-request-trend",
        "height": "stretch",
        "gap": None,
    }
    assert "Requests &lt; placements" in captured["markup"]
    assert "Monthly requests &amp; completed placements." in captured["markup"]
    assert captured["markup_options"] == {"unsafe_allow_html": True}
    assert captured["body_rendered"] is True


def test_chart_title_can_be_suppressed_without_changing_the_plot(monkeypatch) -> None:
    title_calls: list[str] = []
    plot_calls: list[object] = []
    frame = pd.DataFrame(
        {
            "month": ["2025-01", "2025-02"],
            "count": [10, 12],
            "metric": ["Requests", "Requests"],
        }
    )
    monkeypatch.setattr(charts, "_chart_title", title_calls.append)
    monkeypatch.setattr(
        charts.st,
        "plotly_chart",
        lambda figure, **options: plot_calls.append((figure, options)),
    )

    charts.render_line(
        frame,
        "month",
        "count",
        "Talent requests and placements",
        color="metric",
        show_title=False,
    )

    assert title_calls == []
    assert len(plot_calls) == 1
    assert plot_calls[0][1] == {
        "width": "stretch",
        "config": {"displayModeBar": False},
    }

    charts.render_line(
        frame,
        "month",
        "count",
        "Talent requests and placements",
        color="metric",
    )

    assert title_calls == ["Talent requests and placements"]
    assert len(plot_calls) == 2


def test_executive_charts_use_surfaces_without_affecting_other_pages() -> None:
    overview = Path("app_pages/executive_overview.py").read_text()

    assert 'st.columns([3, 2], gap="medium")' in overview
    assert overview.count("with chart_surface(") == 4
    assert overview.count("show_title=False") == 4

    for page in Path("app_pages").glob("*.py"):
        if page.name != "executive_overview.py":
            assert "chart_surface" not in page.read_text()


def test_chart_surface_styles_are_scoped_and_neutral() -> None:
    theme = Path("config/theme.py").read_text()

    assert '[class*="st-key-cds-chart-surface-"]' in theme
    assert "background: #ffffff;" in theme
    assert "border-color: #e0e0e0 !important;" in theme
    assert "border-radius: 0 !important;" in theme
    assert "box-shadow: none !important;" in theme
    assert ".cds-chart-surface__title" in theme
    assert ".cds-chart-surface__description" in theme
    assert "gradient" not in theme
