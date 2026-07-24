"""Shared, presentation-only transformations for dashboard chart data."""

from collections.abc import Mapping, Sequence

import pandas as pd


REQUEST_LABEL_COLUMN = "chart_label"


def with_request_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Add a stable, unique request label without changing the source fields."""
    result = frame.copy()
    company = result["company_name"].fillna("Unknown company").astype(str)
    position = result["nama_posisi"].fillna("Unknown position").astype(str)
    request_id = result["id_talent_req"].fillna("Unknown request").astype(str)
    result[REQUEST_LABEL_COLUMN] = company + " / " + position + " · " + request_id
    return result


def ordered_counts(
    values: pd.Series,
    order: Sequence[str],
    value_name: str = "count",
) -> pd.DataFrame:
    """Return observed categories in an explicit order, without synthetic zeros."""
    counts = values.dropna().astype(str).value_counts()
    observed = set(counts.index)
    ordered = [category for category in order if category in observed]
    ordered.extend(category for category in counts.index if category not in order)
    return pd.DataFrame(
        {
            "category": ordered,
            value_name: [int(counts[category]) for category in ordered],
        }
    )


def monthly_counts(
    frames: Mapping[str, tuple[pd.DataFrame, str]],
    value_name: str,
) -> pd.DataFrame:
    """Create one complete chronological monthly domain for multiple series."""
    series_frames: list[pd.DataFrame] = []
    all_periods: list[pd.Period] = []
    for metric, (frame, date_column) in frames.items():
        if frame.empty or date_column not in frame.columns:
            continue
        dates = pd.to_datetime(frame[date_column], errors="coerce").dropna()
        if dates.empty:
            continue
        periods = dates.dt.to_period("M")
        all_periods.extend(periods.tolist())
        counts = periods.value_counts().rename(value_name).rename_axis("period").reset_index()
        counts["metric"] = metric
        series_frames.append(counts)

    if not all_periods:
        return pd.DataFrame(columns=["month", value_name, "metric"])

    domain = pd.period_range(min(all_periods), max(all_periods), freq="M")
    complete: list[pd.DataFrame] = []
    for metric in frames:
        current = next((item for item in series_frames if item["metric"].iat[0] == metric), None)
        if current is None:
            continue
        current = current.set_index("period")[value_name].reindex(domain, fill_value=0)
        complete.append(
            pd.DataFrame(
                {
                    "month": domain.strftime("%b %Y"),
                    value_name: current.astype(int).to_numpy(),
                    "metric": metric,
                }
            )
        )
    return pd.concat(complete, ignore_index=True)
