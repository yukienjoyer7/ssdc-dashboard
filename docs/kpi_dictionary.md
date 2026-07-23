# SSDC Dashboard KPI Contract

This dashboard follows the v2 canonical KPI dictionary. Rates use explicit
denominators and all age/freshness metrics use the dataset `as_of_date`, not the
current system date.

| ID | KPI | Definition |
| --- | --- | --- |
| KPI-01 | Total Companies | Distinct `id_company` from `COMPANY` |
| KPI-02 | Total Talent Requests | Distinct `id_talent_req` from `TALENT_REQUEST` |
| KPI-03 | Requested Headcount | Sum of request `headcount` at request grain |
| KPI-04 | Candidate Applications | Count of `TRACKING_STUDENT` process rows |
| KPI-05 | Unique Candidates | Distinct NIM among filtered selection processes |
| KPI-06 | Placements | Count of selection rows with canonical outcome `Placement` |
| KPI-07 | Placement Rate | `Placements / Candidate Applications` |
| KPI-08 | Ghosting Rate | `Ghosting / Candidate Applications` |
| KPI-09 | Fulfillment Rate | `Placements / Requested Headcount` via `compute_fulfillment_rate()` |
| KPI-10 | Headcount Gap | `max(requested_headcount - placements, 0)` via `compute_headcount_gap()` |
| KPI-11 | Request Aging | `as_of_date - request_date` via `compute_request_aging()` |
| KPI-12 | Selection Aging | `as_of_date - last_update` |
| KPI-13 | Sync Freshness | `as_of_date - sync_date` |

## Current integration notes

- `as_of_date` is the maximum relevant date across the six cleaned tables.
- Source outcomes are normalized to `Placement`, `Rejected`, `Ghosting`, or
  `On Progress`; the mapping remains conditional on the upstream audit.
- Request action labels are `Belum Dikirim`, `Kurang Kandidat`,
  `Belum Terpenuhi`, `Terpenuhi`, and `Closed`.
- Semantic relevance ranking is not implemented by this KPI change. The
  matching page's current rule-based score remains explicitly provisional.
