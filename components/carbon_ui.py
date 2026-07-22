from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import pandas as pd

from data.contracts import FilterState
from data.loaders import DashboardData
from services.analytics import (
    company_options,
    date_bounds,
    placement_type_options,
    request_status_options,
    study_program_options,
)


def _render_surface(view: str, data: dict[str, Any], *, key: str) -> dict[str, Any] | None:
    """Render the packaged component lazily so pure helpers remain unit-testable."""
    from ssdc_carbon_components import render_surface

    return render_surface(view, data, key=key)


@dataclass(frozen=True)
class PageSpec:
    slug: str
    title: str
    icon: str
    path: str


PAGE_SPECS = (
    PageSpec("executive-overview", "Executive overview", "monitoring", "app_pages/executive_overview.py"),
    PageSpec("talent-request-management", "Talent request management", "task_alt", "app_pages/talent_request_management.py"),
    PageSpec("talent-matching", "Talent matching", "person_search", "app_pages/talent_matching.py"),
    PageSpec("selection-monitoring", "Selection monitoring", "notifications_active", "app_pages/selection_monitoring.py"),
    PageSpec("placement-performance", "Placement performance", "insights", "app_pages/placement_performance.py"),
)


ALL_FILTER_VALUES = {
    "company": "All companies",
    "study_program": "All study programs",
    "request_status": "All request statuses",
    "placement_type": "All placement types",
}


def page_spec_for_title(title: str) -> PageSpec:
    return next((page for page in PAGE_SPECS if page.title == title), PAGE_SPECS[0])


def page_spec_for_slug(slug: str) -> PageSpec | None:
    return next((page for page in PAGE_SPECS if page.slug == slug), None)


def render_shell(active_page: str, *, key: str = "carbon-shell") -> dict[str, Any] | None:
    return _render_surface(
        "shell",
        {
            "pages": [
                {"slug": page.slug, "title": page.title, "icon": page.icon}
                for page in PAGE_SPECS
            ],
            "active_page": active_page,
        },
        key=key,
    )


def default_filters(data: DashboardData) -> FilterState:
    start, end = date_bounds(data)
    return FilterState(date_start=start, date_end=end, **ALL_FILTER_VALUES)


def _option_values(values: list[str], all_label: str) -> list[dict[str, str]]:
    return [{"value": value, "label": value} for value in [all_label, *values]]


def _date_value(value: Any, fallback: date | None) -> date | None:
    if not value:
        return fallback
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return fallback


def _filter_state(payload: dict[str, Any], fallback: FilterState) -> FilterState:
    return FilterState(
        date_start=_date_value(payload.get("date_start"), fallback.date_start),
        date_end=_date_value(payload.get("date_end"), fallback.date_end),
        company=str(payload.get("company") or fallback.company),
        study_program=str(payload.get("study_program") or fallback.study_program),
        request_status=str(payload.get("request_status") or fallback.request_status),
        placement_type=str(payload.get("placement_type") or fallback.placement_type),
    )


def render_filter_toolbar(
    data: DashboardData,
    current: FilterState,
    *,
    key: str = "carbon-filters",
) -> FilterState:
    action = _render_surface(
        "filters",
        {
            "filters": {
                "date_start": current.date_start.isoformat() if current.date_start else "",
                "date_end": current.date_end.isoformat() if current.date_end else "",
                "company": current.company,
                "study_program": current.study_program,
                "request_status": current.request_status,
                "placement_type": current.placement_type,
            },
            "options": {
                "company": _option_values(company_options(data), ALL_FILTER_VALUES["company"]),
                "study_program": _option_values(study_program_options(data), ALL_FILTER_VALUES["study_program"]),
                "request_status": _option_values(request_status_options(data), ALL_FILTER_VALUES["request_status"]),
                "placement_type": _option_values(placement_type_options(data), ALL_FILTER_VALUES["placement_type"]),
            },
        },
        key=key,
    )
    if not action:
        return current
    if action.get("type") == "reset_filters":
        return default_filters(data)
    if action.get("type") == "apply_filters":
        payload = action.get("filters")
        if isinstance(payload, dict):
            return _filter_state(payload, current)
    return current


def render_kpi_row(items: list[dict[str, str]], *, key: str) -> None:
    _render_surface("kpis", {"items": items}, key=key)


def render_feedback(
    title: str,
    detail: str,
    *,
    kind: str = "info",
    key: str,
) -> None:
    _render_surface(
        "feedback",
        {"title": title, "subtitle": detail, "kind": kind},
        key=key,
    )


def render_table(
    frame,
    *,
    columns: list[tuple[str, str]],
    key: str,
    empty_title: str = "No records match",
    empty_detail: str = "Adjust the active filters and try again.",
) -> dict[str, Any] | None:
    safe_columns = [key for key, _ in columns]
    rows = []
    for record in frame[safe_columns].to_dict("records"):
        rows.append({column: _json_safe(value) for column, value in record.items()})
    return _render_surface(
        "table",
        {
            "columns": [{"key": column, "label": label} for column, label in columns],
            "rows": rows,
            "empty_title": empty_title,
            "empty_detail": empty_detail,
        },
        key=key,
    )


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
