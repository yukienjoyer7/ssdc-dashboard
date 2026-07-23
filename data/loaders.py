from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import streamlit as st

from config.settings import resolve_data_dir
from data.contracts import TABLE_FILES, missing_columns
from data.mock_data import build_mock_tables

_PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
_ANALYTIC_FILES = {
    "df_student_profile": "df_student_profile.parquet",
    "df_request": "df_request.parquet",
    "df_selection": "df_selection.parquet",
    "df_company_performance": "df_company_performance.parquet",
}


@dataclass(frozen=True)
class DashboardData:
    tables: dict[str, pd.DataFrame]
    source: str
    is_mock: bool
    warnings: tuple[str, ...] = ()
    analytic_tables: dict[str, pd.DataFrame] = field(default_factory=dict)

    def table(self, name: str) -> pd.DataFrame:
        return self.tables[name].copy()

    def analytic(self, name: str) -> pd.DataFrame | None:
        frame = self.analytic_tables.get(name)
        return frame.copy() if frame is not None else None


def _read_tables(data_dir: Path) -> tuple[dict[str, pd.DataFrame] | None, list[str]]:
    warnings: list[str] = []
    if not data_dir.exists():
        return None, [f"Cleaned data directory not found: {data_dir}"]

    tables: dict[str, pd.DataFrame] = {}
    for filename in TABLE_FILES:
        path = data_dir / filename
        if not path.exists():
            warnings.append(f"Missing table: {filename}")
            continue
        try:
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
        except Exception as exc:  # pragma: no cover - defensive app boundary
            warnings.append(f"Could not read {filename}: {exc}")
            continue
        missing = missing_columns(filename, list(frame.columns))
        if missing:
            warnings.append(f"{filename} is missing columns: {', '.join(missing)}")
        else:
            tables[filename] = frame

    if len(tables) != len(TABLE_FILES):
        return None, warnings or ["The cleaned data contract is incomplete."]
    return tables, warnings


def _load_analytic_tables() -> dict[str, pd.DataFrame]:
    if not _PROCESSED_DIR.exists():
        return {}
    tables: dict[str, pd.DataFrame] = {}
    for key, filename in _ANALYTIC_FILES.items():
        path = _PROCESSED_DIR / filename
        if not path.exists():
            return {}
        tables[key] = pd.read_parquet(path)
    return tables


@st.cache_data(show_spinner=False)
def load_dashboard_data(data_dir: str | None = None) -> DashboardData:
    resolved = Path(data_dir).expanduser().resolve() if data_dir else resolve_data_dir()
    tables, warnings = _read_tables(resolved)
    if tables is not None:
        analytic_tables = _load_analytic_tables()
        return DashboardData(
            tables=tables,
            source=str(resolved),
            is_mock=False,
            warnings=tuple(warnings),
            analytic_tables=analytic_tables,
        )
    fallback_warning = tuple(warnings) + ("Showing anonymized deterministic preview data.",)
    return DashboardData(tables=build_mock_tables(), source="Built-in anonymized preview", is_mock=True, warnings=fallback_warning)
