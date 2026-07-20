"""Build analytical tables from validated cleaned CSVs and save as Parquet.

Grain per table:
  - df_student_profile:       one row per NIM
  - df_request:               one row per id_talent_req x id_tracking_company
  - df_selection:             one row per id_tracking_student
  - df_company_performance:   one row per id_company

All aging/freshness values use the dataset as_of_date, not TODAY().
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from config.settings import resolve_data_dir
from data.contracts import EXPECTED_COLUMNS, TABLE_FILES

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

_OUTCOME_MAP: dict[str, str] = {
    "Placement": "Placement",
    "Rejected": "Rejected",
    "Ghosting": "Ghosting",
    "Finish": "On Progress",
}
_OVERDUE_DAYS = 14

_DATE_COLUMNS = (
    ("company.csv", "created_at"),
    ("talent_request.csv", "request_date"),
    ("tracking_company.csv", "request_date"),
    ("tracking_company.csv", "send_date"),
    ("tracking_student.csv", "last_update"),
    ("status_student.csv", "sync_date"),
)


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def _dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def _compute_as_of_date(tables: dict[str, pd.DataFrame]) -> pd.Timestamp:
    values: list[pd.Timestamp] = []
    for table_name, column in _DATE_COLUMNS:
        if table_name not in tables:
            continue
        values.extend(_dates(tables[table_name][column]).dropna().tolist())
    if not values:
        return pd.NaT
    return max(values)


def _resolve_outcome(row: pd.Series) -> str:
    rejection = row.get("rejection")
    if pd.notna(rejection) and str(rejection).strip():
        value = str(rejection).strip()
        if value == "Placement":
            return "Placement"
        if value == "Ghosting":
            return "Ghosting"
        if value == "On Progress":
            pass
        elif value.startswith("Rejection"):
            return "Rejected"
    progress = row.get("progress_student", "")
    return _OUTCOME_MAP.get(str(progress).strip(), "On Progress")


def _drop_columns(frame: pd.DataFrame, *columns: str) -> pd.DataFrame:
    existing = [col for col in columns if col in frame.columns]
    return frame.drop(columns=existing)


def build_student_profile(students: pd.DataFrame, statuses: pd.DataFrame) -> pd.DataFrame:
    frame = students.merge(statuses, on="NIM", how="left", validate="one_to_one", suffixes=("", "_status"))
    frame["semester"] = _numeric(frame["semester"])
    frame["IPK"] = _numeric(frame["IPK"])
    frame["sync_date"] = _dates(frame["sync_date"])
    frame = _drop_columns(
        frame,
        "hp",
        "email_pribadi",
        "email_kampus",
        "email",
        "no_whatsapp",
        "bulan_masuk",
        "bulan_masuk_month",
        "bulan_masuk_year",
        "id_status",
    )
    columns = [
        "NIM",
        "nama",
        "program_studi",
        "semester",
        "bidang_minat",
        "jenis_penempatan_diminati",
        "status",
        "ketersediaan",
        "CV",
        "portofolio",
        "IPK",
        "domisili",
        "tools",
        "tools_normalized",
        "eligible",
        "sync_date",
        "placement_verified",
    ]
    return frame[[col for col in columns if col in frame.columns]].reset_index(drop=True)


def build_request_table(
    requests: pd.DataFrame,
    tracking_company: pd.DataFrame,
    tracking_student: pd.DataFrame,
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    placements = (
        tracking_student.loc[tracking_student["progress_student"].eq("Placement")]
        .groupby("id_tracking_company", as_index=False)
        .size()
        .rename(columns={"size": "placements"})
    )
    applications = (
        tracking_student.groupby("id_tracking_company", as_index=False)
        .size()
        .rename(columns={"size": "candidate_applications"})
    )
    tracking = tracking_company[
        [
            "id_tracking_company",
            "id_talent_req",
            "nama_perusahaan",
            "progress",
            "send_date",
            "jumlah_permintaan",
            "jumlah_dikirimkan",
            "request_date",
            "list_nim",
        ]
    ].rename(
        columns={
            "nama_perusahaan": "tracker_company",
            "progress": "request_status",
            "request_date": "tracker_request_date",
        }
    )
    frame = requests.merge(tracking, on="id_talent_req", how="left", validate="many_to_one")
    frame = frame.merge(placements, on="id_tracking_company", how="left")
    frame = frame.merge(applications, on="id_tracking_company", how="left")
    frame["company_name"] = frame["nama_perusahaan"].fillna(frame["id_company"])
    frame["request_status"] = frame["request_status"].fillna("Untracked")
    frame["request_date"] = _dates(frame["request_date"]).fillna(_dates(frame["tracker_request_date"]))
    frame["send_date"] = _dates(frame["send_date"])
    frame["requested_headcount"] = _numeric(frame["headcount"])
    frame["candidates_sent"] = _numeric(frame["jumlah_dikirimkan"])
    frame["candidate_applications"] = _numeric(frame["candidate_applications"])
    frame["placements"] = _numeric(frame["placements"])
    frame["headcount_gap"] = (frame["requested_headcount"] - frame["placements"]).clip(lower=0)
    frame["candidate_supply_ratio"] = (
        frame["candidate_applications"] / frame["requested_headcount"].replace(0, pd.NA)
    )
    frame["candidate_supply_ratio"] = frame["candidate_supply_ratio"].fillna(0)
    if not pd.isna(as_of):
        frame["request_aging_days"] = (as_of - frame["request_date"]).dt.days.clip(lower=0)
    else:
        frame["request_aging_days"] = 0
    frame["overdue"] = frame["request_aging_days"] > _OVERDUE_DAYS
    frame["action_label"] = "Terpenuhi"
    frame.loc[frame["request_status"] == "Closed", "action_label"] = "Closed"
    frame.loc[
        (frame["request_status"] != "Closed") & frame["candidate_applications"].eq(0),
        "action_label",
    ] = "Belum Dikirim"
    frame.loc[
        (frame["request_status"] != "Closed")
        & frame["candidate_applications"].gt(0)
        & frame["candidate_applications"].lt(frame["requested_headcount"]),
        "action_label",
    ] = "Kurang Kandidat"
    frame.loc[
        (frame["request_status"] != "Closed")
        & frame["candidate_applications"].ge(frame["requested_headcount"])
        & frame["headcount_gap"].gt(0),
        "action_label",
    ] = "Belum Terpenuhi"
    frame = _drop_columns(
        frame,
        "headcount",
        "jumlah_permintaan",
        "jumlah_dikirimkan",
        "tracker_request_date",
        "tracker_company",
        "sumber_baris_form",
        "alamat_kantor",
        "industri_sektor",
    )
    columns = [
        "id_talent_req",
        "id_tracking_company",
        "id_company",
        "company_name",
        "nama_posisi",
        "jenis_penempatan",
        "requested_headcount",
        "request_status",
        "request_date",
        "send_date",
        "candidates_sent",
        "candidate_applications",
        "placements",
        "headcount_gap",
        "candidate_supply_ratio",
        "request_aging_days",
        "overdue",
        "action_label",
        "bidang_studi_dibutuhkan",
        "bidang_studi_dibutuhkan_normalized",
        "minimum_semester",
        "deskripsi_requirement",
        "working_arrangement",
        "working_arrangement_detail",
        "durasi",
        "durasi_months",
        "renumerasi",
        "renumerasi_category",
        "list_nim",
        "nama_perusahaan",
        "nama_pic",
    ]
    return frame[[col for col in columns if col in frame.columns]].reset_index(drop=True)


def build_selection_table(
    tracking_student: pd.DataFrame,
    tracking_company: pd.DataFrame,
    status_student: pd.DataFrame,
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    tracking = tracking_company[
        [
            "id_tracking_company",
            "id_talent_req",
            "id_company",
            "nama_perusahaan",
            "progress",
            "jenis_penempatan",
        ]
    ].rename(columns={"nama_perusahaan": "request_company", "progress": "request_progress", "jenis_penempatan": "request_placement_type"})
    status = status_student[["NIM", "program_studi", "ketersediaan", "status"]].drop_duplicates("NIM")
    frame = tracking_student.merge(tracking, on="id_tracking_company", how="left", validate="many_to_one")
    frame = frame.merge(status, on="NIM", how="left")
    frame["company_name"] = frame["company"].fillna(frame["request_company"])
    frame["study_program"] = frame["program_studi"].fillna("Unknown")
    frame["placement_type"] = frame["jenis_penempatan"].fillna(frame["request_placement_type"])
    frame["last_update"] = _dates(frame["last_update"])
    frame["canonical_outcome"] = frame.apply(_resolve_outcome, axis=1)
    if not pd.isna(as_of):
        frame["selection_aging_days"] = (as_of - frame["last_update"]).dt.days.clip(lower=0)
    else:
        frame["selection_aging_days"] = 0
    frame["stale_flag"] = frame["selection_aging_days"] > _OVERDUE_DAYS
    frame["follow_up_overdue"] = frame["stale_flag"] & frame["canonical_outcome"].eq("On Progress")
    frame["ghosting_warning"] = frame["canonical_outcome"].eq("Ghosting")
    frame = _drop_columns(
        frame,
        "company",
        "request_company",
        "request_progress",
        "request_placement_type",
        "jenis_penempatan",
    )
    columns = [
        "id_tracking_student",
        "NIM",
        "id_tracking_company",
        "id_talent_req",
        "id_company",
        "student_name",
        "company_name",
        "position",
        "internship_semester",
        "study_program",
        "placement_type",
        "progress_student",
        "canonical_outcome",
        "last_update",
        "selection_aging_days",
        "stale_flag",
        "follow_up_overdue",
        "ghosting_warning",
        "rejection",
        "ketersediaan",
        "status",
    ]
    return frame[[col for col in columns if col in frame.columns]].reset_index(drop=True)


def build_company_performance(
    df_request: pd.DataFrame,
    df_selection: pd.DataFrame,
) -> pd.DataFrame:
    if "id_company" not in df_request.columns or "company_name" not in df_request.columns:
        return pd.DataFrame()
    company_requests = df_request.groupby(["id_company", "company_name"], as_index=False).agg(
        total_requests=("id_talent_req", "nunique"),
        requested_headcount=("requested_headcount", "max"),
        candidates_sent=("candidates_sent", "sum"),
        candidate_applications=("candidate_applications", "sum"),
        placements=("placements", "sum"),
    )
    if "id_company" in df_selection.columns:
        selection_agg = df_selection.groupby("id_company", as_index=False).agg(
            ghosting=("ghosting_warning", lambda s: s.eq(True).sum()),
            rejected=("canonical_outcome", lambda s: s.eq("Rejected").sum()),
        )
        company_requests = company_requests.merge(selection_agg, on="id_company", how="left")
    else:
        company_requests["ghosting"] = 0
        company_requests["rejected"] = 0
    company_requests["ghosting"] = company_requests["ghosting"].fillna(0).astype(int)
    company_requests["rejected"] = company_requests["rejected"].fillna(0).astype(int)
    apps = company_requests["candidate_applications"]
    company_requests["placement_rate"] = (
        (company_requests["placements"] / apps.replace(0, pd.NA) * 100).fillna(0).round(1)
    )
    company_requests["ghosting_rate"] = (
        (company_requests["ghosting"] / apps.replace(0, pd.NA) * 100).fillna(0).round(1)
    )
    company_requests["rejection_rate"] = (
        (company_requests["rejected"] / apps.replace(0, pd.NA) * 100).fillna(0).round(1)
    )
    headcount = company_requests["requested_headcount"]
    company_requests["fulfillment_rate"] = (
        (company_requests["placements"] / headcount.replace(0, pd.NA) * 100).fillna(0).round(1)
    )
    columns = [
        "id_company",
        "company_name",
        "total_requests",
        "requested_headcount",
        "candidates_sent",
        "candidate_applications",
        "placements",
        "placement_rate",
        "ghosting",
        "ghosting_rate",
        "rejected",
        "rejection_rate",
        "fulfillment_rate",
    ]
    return company_requests[[col for col in columns if col in company_requests.columns]].reset_index(drop=True)


def _load_table(data_dir: Path, filename: str) -> pd.DataFrame:
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Required table not found: {path}")
    return pd.read_csv(path, dtype=str, encoding="utf-8-sig")


def _validate_columns(table_name: str, frame: pd.DataFrame) -> None:
    expected = set(EXPECTED_COLUMNS.get(table_name, []))
    actual = set(frame.columns)
    missing = sorted(expected - actual)
    if missing:
        raise ValueError(f"{table_name} is missing columns: {', '.join(missing)}")


def build_all(data_dir: str | Path | None = None) -> dict[str, Any]:
    resolved = Path(data_dir).expanduser().resolve() if data_dir else resolve_data_dir()
    tables: dict[str, pd.DataFrame] = {}
    for filename in TABLE_FILES:
        frame = _load_table(resolved, filename)
        _validate_columns(filename, frame)
        tables[filename] = frame
    as_of = _compute_as_of_date(tables)
    as_of_label = as_of.date().isoformat() if not pd.isna(as_of) else "Unavailable"
    df_student_profile = build_student_profile(
        tables["student_all.csv"], tables["status_student.csv"]
    )
    df_request = build_request_table(
        tables["talent_request.csv"],
        tables["tracking_company.csv"],
        tables["tracking_student.csv"],
        as_of,
    )
    df_selection = build_selection_table(
        tables["tracking_student.csv"],
        tables["tracking_company.csv"],
        tables["status_student.csv"],
        as_of,
    )
    df_company_performance = build_company_performance(df_request, df_selection)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    tables_to_save: dict[str, pd.DataFrame] = {
        "df_student_profile": df_student_profile,
        "df_request": df_request,
        "df_selection": df_selection,
        "df_company_performance": df_company_performance,
    }
    for name, table in tables_to_save.items():
        path = PROCESSED_DIR / f"{name}.parquet"
        table.to_parquet(path, index=False)
    metadata = {
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "as_of_date": as_of_label,
        "source_dir": str(resolved),
        "row_counts": {name: len(table) for name, table in tables_to_save.items()},
        "columns": {name: list(table.columns) for name, table in tables_to_save.items()},
    }
    metadata_path = PROCESSED_DIR / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))
    return metadata


if __name__ == "__main__":
    result = build_all()
    print(json.dumps(result, indent=2, ensure_ascii=False))
