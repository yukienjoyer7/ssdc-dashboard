from datetime import date

import pandas as pd

from data.contracts import FilterState
from data.loaders import DashboardData


TERMINAL_SELECTION_STAGES = {"Rejected", "Finish", "Placement"}
PROTOTYPE_OVERDUE_DAYS = 14
CANONICAL_OUTCOME_MAP = {
    "Placement": "Placement",
    "Rejected": "Rejected",
    "Ghosting": "Ghosting",
    "Finish": "On Progress",
}


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def _dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def dataset_as_of_date(data: DashboardData) -> pd.Timestamp:
    """Return the reproducible maximum relevant date across the six tables."""
    date_columns = (
        ("company.csv", "created_at"),
        ("talent_request.csv", "request_date"),
        ("tracking_company.csv", "request_date"),
        ("tracking_company.csv", "send_date"),
        ("tracking_student.csv", "last_update"),
        ("status_student.csv", "sync_date"),
    )
    values: list[pd.Timestamp] = []
    for table_name, column in date_columns:
        values.extend(_dates(data.table(table_name)[column]).dropna().tolist())
    return max(values) if values else pd.NaT


def _canonical_outcome(frame: pd.DataFrame) -> pd.Series:
    """Resolve canonical outcome using rejection as source of truth, fallback to progress_student."""
    result = frame["progress_student"].map(CANONICAL_OUTCOME_MAP).fillna("On Progress")
    mask = frame["rejection"].notna() & (frame["rejection"].astype(str).str.strip() != "")
    if not mask.any():
        return result
    rejection_values = frame.loc[mask, "rejection"].astype(str).str.strip()
    result.loc[mask & rejection_values.eq("Placement")] = "Placement"
    result.loc[mask & rejection_values.eq("Ghosting")] = "Ghosting"
    result.loc[mask & rejection_values.str.startswith("Rejection")] = "Rejected"
    return result


def compute_request_aging(request_date: pd.Series, as_of: pd.Timestamp) -> pd.Series:
    dates = _dates(request_date)
    if pd.isna(as_of):
        return pd.Series(0, index=dates.index)
    return (as_of - dates).dt.days.clip(lower=0).fillna(0).astype(int)


def compute_headcount_gap(requested_headcount: pd.Series, placements: pd.Series) -> pd.Series:
    return (_numeric(requested_headcount) - _numeric(placements)).clip(lower=0).astype(int)


def compute_fulfillment_rate(placements: pd.Series, requested_headcount: pd.Series) -> pd.Series:
    pl = _numeric(placements)
    hc = _numeric(requested_headcount)
    return (pl / hc.replace(0, pd.NA) * 100).fillna(0)


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
    frame = data.analytic("df_request")
    if frame is not None:
        frame["request_date"] = _dates(frame["request_date"])
        frame["aging_days"] = frame["request_aging_days"]
        frame = _apply_date_filter(frame, "request_date", filters)
        frame = _apply_company(frame, filters)
        if filters.request_status != "All request statuses":
            frame = frame.loc[frame["request_status"] == filters.request_status].copy()
        return frame.sort_values(["headcount_gap", "request_aging_days"], ascending=False).reset_index(drop=True)

    requests = data.table("talent_request.csv")
    tracking = data.table("tracking_company.csv")
    selection = data.table("tracking_student.csv")

    placements = (
        selection.loc[selection["progress_student"].eq("Placement")]
        .groupby("id_tracking_company", as_index=False)
        .size()
        .rename(columns={"size": "placements"})
    )
    applications = (
        selection.groupby("id_tracking_company", as_index=False)
        .size()
        .rename(columns={"size": "candidate_applications"})
    )
    tracking_columns = [
        "id_talent_req", "id_tracking_company", "progress", "jumlah_dikirimkan",
        "jumlah_permintaan", "request_date", "send_date",
    ]
    frame = requests.merge(tracking[tracking_columns], on="id_talent_req", how="left", suffixes=("", "_tracking"))
    frame = frame.merge(placements, on="id_tracking_company", how="left")
    frame = frame.merge(applications, on="id_tracking_company", how="left")
    frame["company_name"] = frame["nama_perusahaan"].fillna(frame["id_company"])
    frame["request_status"] = frame["progress"].fillna("Untracked")
    frame["request_date"] = frame["request_date"].fillna(frame["request_date_tracking"])
    frame["requested_headcount"] = _numeric(frame["headcount"])
    frame["candidates_sent"] = _numeric(frame["jumlah_dikirimkan"])
    frame["candidate_applications"] = _numeric(frame["candidate_applications"])
    frame["placements"] = _numeric(frame["placements"])
    frame["headcount_gap"] = compute_headcount_gap(
        frame["requested_headcount"],
        frame.groupby("id_talent_req")["placements"].transform("sum"),
    )
    frame["candidate_supply_ratio"] = (
        frame["candidate_applications"].div(frame["requested_headcount"].replace(0, pd.NA)).fillna(0)
    )
    reference = dataset_as_of_date(data)
    frame["request_aging_days"] = compute_request_aging(frame["request_date"], reference)
    frame["aging_days"] = frame["request_aging_days"]
    frame["overdue"] = frame["request_aging_days"] > PROTOTYPE_OVERDUE_DAYS
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
    frame = _apply_date_filter(frame, "request_date", filters)
    frame = _apply_company(frame, filters)
    if filters.request_status != "All request statuses":
        frame = frame.loc[frame["request_status"] == filters.request_status].copy()
    return frame.sort_values(["headcount_gap", "request_aging_days"], ascending=False).reset_index(drop=True)


def selection_table(data: DashboardData, filters: FilterState) -> pd.DataFrame:
    frame = data.analytic("df_selection")
    if frame is not None:
        frame["stage_aging_days"] = frame["selection_aging_days"]
        frame["last_update"] = _dates(frame["last_update"])
        frame = _apply_date_filter(frame, "last_update", filters)
        frame = _apply_company(frame, filters)
        if filters.study_program != "All study programs":
            frame = frame.loc[frame["study_program"] == filters.study_program].copy()
        if filters.placement_type != "All placement types":
            frame = frame.loc[frame["placement_type"] == filters.placement_type].copy()
        if filters.request_status != "All request statuses":
            frame = frame.loc[frame["request_status"] == filters.request_status].copy()
        return frame.sort_values(["ghosting_warning", "stale_flag", "selection_aging_days"], ascending=False).reset_index(drop=True)

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
    frame["canonical_outcome"] = _canonical_outcome(frame)
    reference = dataset_as_of_date(data)
    frame["selection_aging_days"] = (reference - frame["last_update"]).dt.days.clip(lower=0)
    frame["stage_aging_days"] = frame["selection_aging_days"]
    frame["stale_flag"] = frame["selection_aging_days"].gt(PROTOTYPE_OVERDUE_DAYS)
    frame["follow_up_overdue"] = (
        frame["stale_flag"] & frame["canonical_outcome"].eq("On Progress")
    )
    frame["ghosting_warning"] = frame["canonical_outcome"].eq("Ghosting")
    frame = _apply_date_filter(frame, "last_update", filters)
    frame = _apply_company(frame, filters)
    if filters.study_program != "All study programs":
        frame = frame.loc[frame["study_program"] == filters.study_program].copy()
    if filters.placement_type != "All placement types":
        frame = frame.loc[frame["placement_type"] == filters.placement_type].copy()
    if filters.request_status != "All request statuses":
        frame = frame.loc[frame["request_status"] == filters.request_status].copy()
    return frame.sort_values(["ghosting_warning", "stale_flag", "selection_aging_days"], ascending=False).reset_index(drop=True)


def placement_table(data: DashboardData, filters: FilterState) -> pd.DataFrame:
    frame = selection_table(data, filters)
    frame = frame.loc[frame["canonical_outcome"].eq("Placement")].copy()
    frame["placement_date"] = frame["last_update"]
    frame["time_to_placement_days"] = frame["stage_aging_days"]
    return frame


def canonical_kpis(data: DashboardData, filters: FilterState) -> dict[str, float | int | str]:
    """Calculate KPI-01 through KPI-13 at their canonical grains."""
    requests = request_table(data, filters).drop_duplicates("id_talent_req")
    selection = selection_table(data, filters)
    companies = data.table("company.csv")
    if filters.company != "All companies":
        companies = companies.loc[companies["company_name"] == filters.company]

    applications = len(selection)
    placements = int(selection["canonical_outcome"].eq("Placement").sum())
    ghosting = int(selection["canonical_outcome"].eq("Ghosting").sum())
    request_ids_in_scope = selection["id_talent_req"].unique()
    scoped_headcount = requests.loc[
        requests["id_talent_req"].isin(request_ids_in_scope), "requested_headcount"
    ].sum()
    as_of = dataset_as_of_date(data)
    sync_dates = _dates(data.table("status_student.csv")["sync_date"])
    sync_freshness = (as_of - sync_dates).dt.days.max() if not pd.isna(as_of) else 0

    return {
        "KPI-01": int(companies["id_company"].nunique()),
        "KPI-02": int(requests["id_talent_req"].nunique()),
        "KPI-03": int(requests["requested_headcount"].sum()),
        "KPI-04": int(applications),
        "KPI-05": int(selection["NIM"].nunique()),
        "KPI-06": placements,
        "KPI-07": placements / applications * 100 if applications else 0,
        "KPI-08": ghosting / applications * 100 if applications else 0,
        "KPI-09": float(compute_fulfillment_rate(pd.Series(placements), pd.Series(scoped_headcount)).iloc[0]),
        "KPI-10": int(requests["headcount_gap"].sum()),
        "KPI-11": float(requests["request_aging_days"].mean()) if not requests.empty else 0,
        "KPI-12": float(selection["selection_aging_days"].mean()) if not selection.empty else 0,
        "KPI-13": int(sync_freshness) if pd.notna(sync_freshness) else 0,
        "as_of_date": as_of.date().isoformat() if not pd.isna(as_of) else "Unavailable",
    }


def matching_table(data: DashboardData, request_id: str, filters: FilterState) -> tuple[pd.DataFrame, pd.Series | None]:
    requests = request_table(data, filters)
    selected = requests.loc[requests["id_talent_req"] == request_id]
    if selected.empty:
        return pd.DataFrame(), None
    request = selected.iloc[0]
    students = data.analytic("df_student_profile")
    if students is not None:
        frame = students.copy()
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
        fallback = date(1970, 1, 1)
        return fallback, fallback
    return min(values).date(), max(values).date()


def company_options(data: DashboardData) -> list[str]:
    return sorted(data.table("company.csv")["company_name"].dropna().unique().tolist())


def study_program_options(data: DashboardData) -> list[str]:
    return sorted(data.table("status_student.csv")["program_studi"].dropna().unique().tolist())


def request_status_options(data: DashboardData) -> list[str]:
    return sorted(data.table("tracking_company.csv")["progress"].dropna().unique().tolist())


def placement_type_options(data: DashboardData) -> list[str]:
    return sorted(data.table("talent_request.csv")["jenis_penempatan"].dropna().unique().tolist())
