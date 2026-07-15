# Prototype Decisions

## Public repository, private data

The GitHub repository is public as requested. The cleaned tables contain names,
emails, phone numbers, and student identifiers, so neither raw nor cleaned CSVs
are committed. Local data is loaded from `SSDC_DATA_DIR`; missing data falls back
to deterministic anonymized rows.

## Provisional analytical rules

The first prototype uses transparent, dashboard-owned previews for rules that
are not yet approved:

- active requests exclude `Closed` and `Draft`;
- request aging uses the selected date-end and a 14-day overdue threshold;
- fulfilment uses `Placement` records linked through tracking-company IDs;
- request priority combines overdue status, headcount gap, and candidate supply;
- matching scores study/interest match, minimum semester, and availability;
- selection aging uses the current record's `last_update` date;
- `Ghosting` source status is surfaced as a warning;
- placement duration and placement date use the current tracking record's last update;
- placement-rate denominator is unique placed candidates in the filtered view.

These rules are presentation previews and must be replaced or approved by the
PM/Data Engineer before final KPI validation.
