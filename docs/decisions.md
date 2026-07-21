# Prototype Decisions

## Public repository, private data

The GitHub repository is public as requested. The cleaned tables contain names,
emails, phone numbers, and student identifiers, so neither raw nor cleaned CSVs
are committed. Local data is loaded from `SSDC_DATA_DIR`; missing data falls back
to deterministic anonymized rows.

## V2 KPI alignment

The dashboard now centralizes KPI-01 through KPI-13 in
`services/analytics.py`:

- placement rate = `Placements / Candidate Applications`;
- ghosting rate = `Ghosting / Candidate Applications`;
- fulfillment rate = `Placements / Requested Headcount`;
- headcount gap = `max(requested_headcount - placements, 0)`;
- request aging and selection aging use the dataset `as_of_date`;
- sync freshness uses `as_of_date - sync_date`;
- request action labels are deterministic and do not use a weighted priority score.

The current source mapping is a dashboard integration contract pending final
Data Engineer approval: `Placement`, `Rejected`, and `Ghosting` retain their
source outcomes; `Finish` and other non-terminal source stages map to
`On Progress`.

## Pure function extraction

Request aging, headcount gap, and fulfillment rate calculations were extracted into
three pure functions in `services/analytics.py` to replace duplicated inline logic
in both `analytics.py` and `analytical_tables.py`:

- `compute_request_aging(request_date, as_of_date)` — `(as_of - request_date).days`, clipped >=0, null-safe
- `compute_headcount_gap(requested_headcount, placements)` — `max(headcount - placements, 0)`, placement values aggregated at request level
- `compute_fulfillment_rate(placements, requested_headcount)` — `placements / headcount * 100`, divide-by-zero returns 0

Tests live in `tests/test_metrics.py`.

## Headcount gap aggregation

The `build_request_table()` ETL previously subtracted row-level placements from
the request headcount. This was inconsistent with the runtime `request_table()` path,
which aggregates placements across all tracking_company rows per request first
(`groupby("id_talent_req")["placements"].transform("sum")`).

Both paths now use the aggregate pattern, ensuring requests with multiple
tracking_company rows produce the same headcount_gap value.


