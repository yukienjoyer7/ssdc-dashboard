import pandas as pd

from services.analytics import (
    compute_fulfillment_rate,
    compute_headcount_gap,
    compute_request_aging,
)


_AS_OF = pd.Timestamp("2026-04-01")


def test_aging_normal() -> None:
    dates = pd.Series(["2026-01-15", "2026-03-01", "2026-04-01"])
    result = compute_request_aging(dates, _AS_OF)
    assert result.tolist() == [76, 31, 0]


def test_aging_null_date() -> None:
    dates = pd.Series(["2026-02-01", None, "2026-03-01"])
    result = compute_request_aging(dates, _AS_OF)
    assert result.tolist() == [59, 0, 31]


def test_aging_future_date_clipped() -> None:
    dates = pd.Series(["2026-05-15", "2026-06-01"])
    result = compute_request_aging(dates, _AS_OF)
    assert (result == 0).all()


def test_aging_nat_as_of() -> None:
    dates = pd.Series(["2026-01-15", "2026-03-01"])
    result = compute_request_aging(dates, pd.NaT)
    assert result.tolist() == [0, 0]


def test_gap_positive() -> None:
    headcount = pd.Series([10, 5, 3])
    placements = pd.Series([3, 2, 0])
    result = compute_headcount_gap(headcount, placements)
    assert result.tolist() == [7, 3, 3]


def test_gap_zero() -> None:
    headcount = pd.Series([5, 3])
    placements = pd.Series([5, 3])
    result = compute_headcount_gap(headcount, placements)
    assert (result == 0).all()


def test_gap_overfilled_clipped() -> None:
    headcount = pd.Series([5, 3])
    placements = pd.Series([7, 4])
    result = compute_headcount_gap(headcount, placements)
    assert (result == 0).all()


def test_gap_null_values() -> None:
    headcount = pd.Series([5, None, 3])
    placements = pd.Series([None, 2, 3])
    result = compute_headcount_gap(headcount, placements)
    assert result.tolist() == [5, 0, 0]


def test_fulfillment_normal() -> None:
    placements = pd.Series([3, 5, 0])
    headcount = pd.Series([10, 10, 10])
    result = compute_fulfillment_rate(placements, headcount)
    assert result.tolist() == [30.0, 50.0, 0.0]


def test_fulfillment_zero_denominator() -> None:
    placements = pd.Series([5, 0])
    headcount = pd.Series([0, 0])
    result = compute_fulfillment_rate(placements, headcount)
    assert result.tolist() == [0.0, 0.0]


def test_fulfillment_overfilled() -> None:
    placements = pd.Series([12, 3])
    headcount = pd.Series([10, 2])
    result = compute_fulfillment_rate(placements, headcount)
    assert result.tolist() == [120.0, 150.0]


def test_fulfillment_null_values() -> None:
    placements = pd.Series([5, None, 3])
    headcount = pd.Series([10, 10, None])
    result = compute_fulfillment_rate(placements, headcount)
    assert result.tolist() == [50.0, 0.0, 0.0]
