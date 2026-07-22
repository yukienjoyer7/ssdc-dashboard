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

Semantic matching remains a separate follow-up integration. The current page's
rule-based prototype score is not treated as a canonical KPI or acceptance
probability until precomputed semantic scores are available upstream.

## Carbon migration architecture

The dashboard uses Carbon Web Components directly through the official
Streamlit Components v2 API. React and CDN dependencies are intentionally not
introduced: the frontend is packaged with the repository and its compiled
assets are included in the Python package.

The migration is deliberately hybrid. Carbon owns navigation, filters, KPI
tiles, feedback states, and table framing, while Plotly remains responsible
for data visualization. This keeps existing chart behavior and analytics
contracts stable while replacing the most visible Streamlit-default surfaces.

Global filters use explicit Apply semantics. The component keeps edits local in
the browser and emits an action only when the user applies or resets filters;
the Python app stores the resulting `FilterState` in session state.
