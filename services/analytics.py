from datetime import date

import pandas as pd

from data.contracts import FilterState
from data.loaders import DashboardData


TERMINAL_SELECTION_STAGES = {"Rejected", "Finish", "Placement"}
PROTOTYPE_OVERDUE_DAYS = 14
PROTOTYPE_STRONG_MATCH_SCORE = 75


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def _dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def _reference_date(filters: FilterState, series: pd.Series) -> pd.Timestamp:
    if filters.date_end:
        return pd.Timestamp(filters.date_end)
    parsed = _dates(series).dropna()
    return parsed.max() if not parsed.empty else pd.Timestamp(date.today())


def _apply_date_filter(frame: pd.DataFrame, column: str, filters: FilterState) -> pd.DataFrame:
    parsed = _dates(frame[column])
    mask = parsed.notna()
    if filters.date_start:
        mask &= parsed.dt.date >= filters.date_start
    if filters.date_end:
        mask &= parsed.dt.date <= filters.date_end
    return frame.loc[mask].copy()


def _apply_company(frame: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    if filters.company == "All companies" or "company_name" not in frame:
        return frame
    return frame.loc[frame["company_name"] == filters.company].copy()


def request_table(data: DashboardData, filters: FilterState) -> pd.DataFrame:
    requests = data.table("talent_request.csv")
    tracking = data.table("tracking_company.csv")
    selection = data.table("tracking_student.csv")

    placements = (
        selection.loc[selection["progress_student"].eq("Placement")]
        .groupby("id_tracking_company", as_index=False)
        .size()
        .rename(columns={"size": "fulfilled_headcount"})
    )
    tracking_columns = [
        "id_talent_req", "id_tracking_company", "progress", "jumlah_dikirimkan",
        "jumlah_permintaan", "request_date", "send_date",
    ]
    frame = requests.merge(tracking[tracking_columns], on="id_talent_req", how="left", suffixes=("", "_tracking"))
    frame = frame.merge(placements, on="id_tracking_company", how="left")
    frame["company_name"] = frame["nama_perusahaan"].fillna(frame["id_company"])
    frame["request_status"] = frame["progress"].fillna("Untracked")
    frame["request_date"] = frame["request_date"].fillna(frame["request_date_tracking"])
    frame["requested_headcount"] = _numeric(frame["headcount"])
    frame["candidates_sent"] = _numeric(frame["jumlah_dikirimkan"])
    frame["fulfilled_headcount"] = _numeric(frame["fulfilled_headcount"])
    frame["headcount_gap"] = (frame["requested_headcount"] - frame["fulfilled_headcount"]).clip(lower=0)
    frame["candidate_supply_ratio"] = (
        frame["candidates_sent"].div(frame["requested_headcount"].replace(0, pd.NA)).fillna(0)
    )
    reference = _reference_date(filters, frame["request_date"])
    frame["aging_days"] = (_dates(frame["request_date"]).rsub(reference).dt.days).clip(lower=0)
    frame["overdue"] = frame["aging_days"] > PROTOTYPE_OVERDUE_DAYS
    frame["priority_score"] = (
        frame["overdue"].astype(int) * 35
        + (frame["headcount_gap"] > 0).astype(int) * 35
        + (frame["candidate_supply_ratio"] < 1).astype(int) * 30
    )
    frame["priority_category"] = "Monitor"
    frame.loc[frame["priority_score"] >= 35, "priority_category"] = "Action"
    frame.loc[frame["priority_score"] >= 70, "priority_category"] = "Urgent"
    frame["priority_reason"] = "No prototype warning condition"
    frame.loc[frame["overdue"], "priority_reason"] = "Request aging exceeds prototype threshold"
    frame.loc[(~frame["overdue"]) & (frame["headcount_gap"] > 0), "priority_reason"] = "Headcount gap remains"
    frame.loc[
        (~frame["overdue"]) & (frame["headcount_gap"] <= 0) & (frame["candidate_supply_ratio"] < 1),
        "priority_reason",
    ] = "Candidate supply below requested headcount"

    frame = _apply_date_filter(frame, "request_date", filters)
    frame = _apply_company(frame, filters)
    if filters.request_status != "All request statuses":
        frame = frame.loc[frame["request_status"] == filters.request_status].copy()
    return frame.sort_values(["priority_score", "aging_days"], ascending=False).reset_index(drop=True)


def selection_table(data: DashboardData, filters: FilterState) -> pd.DataFrame:
    selection = data.table("tracking_student.csv")
    tracking = data.table("tracking_company.csv")
    status = data.table("status_student.csv")
    tracking_fields = tracking[["id_tracking_company", "id_talent_req", "id_company", "nama_perusahaan", "progress", "jenis_penempatan"]]
    status_fields = status[["NIM", "program_studi", "ketersediaan", "status"]].drop_duplicates("NIM")
    frame = selection.merge(tracking_fields, on="id_tracking_company", how="left", suffixes=("", "_request"))
    frame = frame.merge(status_fields, on="NIM", how="left")
    frame["company_name"] = frame["company"].fillna(frame["nama_perusahaan"])
    frame["request_status"] = frame["progress"].fillna("Untracked")
    frame["study_program"] = frame["program_studi"].fillna("Unknown")
    frame["placement_type"] = frame["jenis_penempatan"].fillna(frame["jenis_penempatan_request"])
    frame["last_update"] = _dates(frame["last_update"])
    reference = _reference_date(filters, frame["last_update"])
    frame["stage_aging_days"] = (reference - frame["last_update"]).dt.days.clip(lower=0)
    frame["follow_up_overdue"] = (
        frame["stage_aging_days"].gt(PROTOTYPE_OVERDUE_DAYS)
        & ~frame["progress_student"].isin(TERMINAL_SELECTION_STAGES)
    )
    frame["ghosting_warning"] = frame["progress_student"].eq("Ghosting")
    frame = _apply_date_filter(frame, "last_update", filters)
    frame = _apply_company(frame, filters)
    if filters.study_program != "All study programs":
        frame = frame.loc[frame["study_program"] == filters.study_program].copy()
    if filters.placement_type != "All placement types":
        frame = frame.loc[frame["placement_type"] == filters.placement_type].copy()
    if filters.request_status != "All request statuses":
        frame = frame.loc[frame["request_status"] == filters.request_status].copy()
    return frame.sort_values(["ghosting_warning", "follow_up_overdue", "stage_aging_days"], ascending=False).reset_index(drop=True)


def placement_table(data: DashboardData, filters: FilterState) -> pd.DataFrame:
    frame = selection_table(data, filters)
    frame = frame.loc[frame["progress_student"].eq("Placement")].copy()
    frame["placement_date"] = frame["last_update"]
    frame["time_to_placement_days"] = frame["stage_aging_days"]
    return frame


def matching_table(data: DashboardData, request_id: str, filters: FilterState) -> tuple[pd.DataFrame, pd.Series | None]:
    requests = request_table(data, filters)
    selected = requests.loc[requests["id_talent_req"] == request_id]
    if selected.empty:
        return pd.DataFrame(), None
    request = selected.iloc[0]
    students = data.table("student_all.csv")
    status = data.table("status_student.csv")[["NIM", "ketersediaan", "status", "IPK"]].drop_duplicates("NIM")
    frame = students.merge(status, on="NIM", how="left")
    if filters.study_program != "All study programs":
        frame = frame.loc[frame["program_studi"] == filters.study_program].copy()
    frame["semester_num"] = _numeric(frame["semester"])
    minimum_semester = float(pd.to_numeric(request["minimum_semester"], errors="coerce") or 0)
    required_terms = [term.strip().lower() for term in str(request["bidang_studi_dibutuhkan"]).split(",") if term.strip()]
    searchable = (frame["program_studi"].fillna("") + " " + frame["bidang_minat"].fillna("")).str.lower()
    frame["study_match"] = searchable.apply(lambda value: any(term in value for term in required_terms))
    frame["semester_match"] = frame["semester_num"] >= minimum_semester
    frame["available_match"] = frame["ketersediaan"].eq("Available")
    frame["eligible"] = frame["study_match"] & frame["semester_match"] & frame["available_match"]
    frame["match_score"] = (
        frame["study_match"].astype(int) * 40
        + frame["semester_match"].astype(int) * 35
        + frame["available_match"].astype(int) * 25
    )
    frame["recommendation"] = "Review"
    frame.loc[frame["eligible"], "recommendation"] = "Strong match"
    frame.loc[(~frame["eligible"]) & (frame["match_score"] >= 40), "recommendation"] = "Potential match"
    frame["explanation"] = frame.apply(_matching_explanation, axis=1)
    return frame.sort_values(["eligible", "match_score", "IPK"], ascending=False).reset_index(drop=True), request


def _matching_explanation(row: pd.Series) -> str:
    matched = []
    missing = []
    for label, key in (("study program", "study_match"), ("semester", "semester_match"), ("availability", "available_match")):
        (matched if row[key] else missing).append(label)
    if not missing:
        return "Matches study program, minimum semester, and availability."
    return f"Matches {', '.join(matched) or 'none'}; review {', '.join(missing)}."


def date_bounds(data: DashboardData) -> tuple[date, date]:
    values: list[pd.Timestamp] = []
    for filename, column in (
        ("talent_request.csv", "request_date"),
        ("tracking_student.csv", "last_update"),
        ("tracking_company.csv", "request_date"),
    ):
        values.extend(_dates(data.table(filename)[column]).dropna().tolist())
    if not values:
        today = date.today()
        return today, today
    return min(values).date(), max(values).date()


def company_options(data: DashboardData) -> list[str]:
    return sorted(data.table("company.csv")["company_name"].dropna().unique().tolist())


def study_program_options(data: DashboardData) -> list[str]:
    return sorted(data.table("status_student.csv")["program_studi"].dropna().unique().tolist())


def request_status_options(data: DashboardData) -> list[str]:
    return sorted(data.table("tracking_company.csv")["progress"].dropna().unique().tolist())


def placement_type_options(data: DashboardData) -> list[str]:
    return sorted(data.table("talent_request.csv")["jenis_penempatan"].dropna().unique().tolist())
