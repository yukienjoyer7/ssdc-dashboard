import pandas as pd

from services.analytics import (
    classify_follow_up,
    classify_ghosting,
    compute_selection_aging,
    resolve_outcome,
)


_AS_OF = pd.Timestamp("2026-04-01")


def test_selection_aging_normal() -> None:
    dates = pd.Series(["2026-01-15", "2026-03-01", "2026-04-01"])
    result = compute_selection_aging(dates, _AS_OF)
    assert result.tolist() == [76, 31, 0]


def test_selection_aging_null_date() -> None:
    dates = pd.Series(["2026-02-01", None, "2026-03-01"])
    result = compute_selection_aging(dates, _AS_OF)
    assert result.tolist() == [59, 0, 31]


def test_selection_aging_future_date_clipped() -> None:
    dates = pd.Series(["2026-05-15", "2026-06-01"])
    result = compute_selection_aging(dates, _AS_OF)
    assert (result == 0).all()


def test_selection_aging_nat_as_of() -> None:
    dates = pd.Series(["2026-01-15", "2026-03-01"])
    result = compute_selection_aging(dates, pd.NaT)
    assert result.tolist() == [0, 0]


def test_outcome_placement_from_rejection() -> None:
    result = resolve_outcome(
        pd.Series(["Finish"]),
        pd.Series(["Placement"]),
    )
    assert result.iloc[0] == "Placement"


def test_outcome_rejected_from_prefix() -> None:
    result = resolve_outcome(
        pd.Series(["Interview User"]),
        pd.Series(["Rejection Interview User"]),
    )
    assert result.iloc[0] == "Rejected"


def test_outcome_ghosting_from_rejection() -> None:
    result = resolve_outcome(
        pd.Series(["Finish"]),
        pd.Series(["Ghosting"]),
    )
    assert result.iloc[0] == "Ghosting"


def test_outcome_falls_back_to_progress() -> None:
    result = resolve_outcome(
        pd.Series(["Finish"]),
        pd.Series([""]),
    )
    assert result.iloc[0] == "On Progress"


def test_outcome_on_progress_pass_through() -> None:
    result = resolve_outcome(
        pd.Series(["Interview User"]),
        pd.Series(["On Progress"]),
    )
    assert result.iloc[0] == "On Progress"


def test_outcome_unknown_progress_defaults_on_progress() -> None:
    result = resolve_outcome(
        pd.Series(["Unknown Stage"]),
        pd.Series([""]),
    )
    assert result.iloc[0] == "On Progress"


def test_classify_ghosting_positive() -> None:
    outcome = pd.Series(["Ghosting", "On Progress", "Placement"])
    result = classify_ghosting(outcome)
    assert result.tolist() == [True, False, False]


def test_classify_ghosting_all_negative() -> None:
    outcome = pd.Series(["On Progress", "Placement", "Rejected"])
    result = classify_ghosting(outcome)
    assert (result == False).all()  # noqa: E712


def test_follow_up_ghosting_priority() -> None:
    outcome = pd.Series(["Ghosting", "Ghosting"])
    stale = pd.Series([True, False])
    stage = pd.Series(["FU 1", "Submitted"])
    result = classify_follow_up(outcome, stale, stage)
    assert result.tolist() == ["Contact student", "Contact student"]


def test_follow_up_escalate() -> None:
    outcome = pd.Series(["On Progress", "On Progress", "On Progress"])
    stale = pd.Series([True, True, True])
    stage = pd.Series(["FU 1", "FU 2", "FU 3"])
    result = classify_follow_up(outcome, stale, stage)
    assert result.tolist() == ["Escalate", "Escalate", "Escalate"]


def test_follow_up_company() -> None:
    outcome = pd.Series(["On Progress", "Rejected"])
    stale = pd.Series([True, True])
    stage = pd.Series(["Submitted", "Interview User"])
    result = classify_follow_up(outcome, stale, stage)
    assert result.tolist() == ["Follow up with company", "Monitor"]


def test_follow_up_default_monitor() -> None:
    outcome = pd.Series(["On Progress", "Placement", "On Progress"])
    stale = pd.Series([False, False, True])
    stage = pd.Series(["Submitted", "Finish", "FU 4"])
    result = classify_follow_up(outcome, stale, stage)
    assert result.tolist() == ["Monitor", "Monitor", "Follow up with company"]


def test_follow_up_ghosting_overrides_stale() -> None:
    outcome = pd.Series(["Ghosting"])
    stale = pd.Series([True])
    stage = pd.Series(["FU 1"])
    result = classify_follow_up(outcome, stale, stage)
    assert result.iloc[0] == "Contact student"
