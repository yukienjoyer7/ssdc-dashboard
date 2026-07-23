from collections.abc import Iterable
from html import escape

import pandas as pd
import streamlit as st

from components.carbon_ui import render_data_status_surface, render_kpi_row
from data.loaders import DashboardData
from services.analytics import dataset_as_of_date


def render_page_header(kicker: str, title: str, question: str) -> None:
    st.markdown(
        '<header class="cds-page-header">'
        f'<p class="cds-kicker">{escape(kicker)}</p>'
        f'<h1 class="cds-page-title">{escape(title)}</h1>'
        f'<p class="cds-page-description">{escape(question)}</p>'
        "</header>",
        unsafe_allow_html=True,
    )


def render_data_status(
    data: DashboardData,
    provisional_note: str,
    *,
    key: str,
) -> None:
    as_of = dataset_as_of_date(data)
    record_count = sum(len(frame) for frame in data.tables.values())
    as_of_label = as_of.date().isoformat() if not pd.isna(as_of) else ""
    validation_note = provisional_note.format(as_of_date=as_of_label or "Unavailable")
    validation_note = f"{validation_note} Pending PM/Data Engineer validation."
    mode_label = "Prototype preview" if data.is_mock else "Local cleaned data"
    render_data_status_surface(
        mode="prototype" if data.is_mock else "local",
        record_count=record_count,
        as_of_date=as_of_label,
        kpi_status="provisional",
        detail_items=[
            {"label": "Mode", "value": mode_label},
            {"label": "Source", "value": data.source},
            {"label": "Records", "value": f"{record_count:,}"},
            {"label": "Dataset as of", "value": as_of_label or "Unavailable"},
            {"label": "KPI status", "value": "Provisional"},
            {"label": "Validation notes", "value": validation_note},
        ],
        warnings=list(data.warnings),
        key=key,
    )


def render_kpis(
    items: Iterable[dict[str, str]],
    columns_per_row: int | None = None,
    key: str | None = None,
    *,
    variant: str = "default",
    section_label: str | None = None,
) -> None:
    items = list(items)
    if not items:
        return
    if variant not in {"default", "primary", "compact"}:
        raise ValueError(f"Unsupported KPI variant: {variant}")
    render_kpi_row(
        items,
        key=key or "carbon-kpis-" + "-".join(item["label"].lower().replace(" ", "-") for item in items),
        variant=variant,
        section_label=section_label,
        columns_per_row=max(1, int(columns_per_row)) if columns_per_row is not None else None,
    )


def render_section(title: str, note: str | None = None) -> None:
    note_html = f'<p class="cds-section-note">{escape(note)}</p>' if note else ""
    st.markdown(
        '<header class="cds-section-header">'
        f'<h2 class="cds-section-heading">{escape(title)}</h2>'
        f"{note_html}"
        "</header>",
        unsafe_allow_html=True,
    )


def format_count(value: float | int) -> str:
    return f"{int(round(value)):,}"


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def format_days(value: float) -> str:
    return f"{value:.0f} days"
