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

## Dimensional performance tables

Four pre-aggregated tables compute placement performance across key
dimensions. Each table uses the same metric set, built by
`_build_dimensional_performance()` in `services/analytical_tables.py`.

| Table | Dimension column | Grain |
| --- | --- | --- |
| `df_program_performance` | `study_program` | One row per study program |
| `df_placement_type_performance` | `placement_type` | One row per placement type |
| `df_sector_performance` | `industry_sector` | One row per industry sector |
| `df_work_arrangement_performance` | `working_arrangement` | One row per working arrangement |

### Shared metrics

| Column | Definition | Denominator |
| --- | --- | --- |
| `total_applications` | Count of `TRACKING_STUDENT` rows per dimension group | — |
| `unique_candidates` | Distinct NIM per dimension group | — |
| `requested_headcount` | Sum of request `headcount` (deduplicated by `id_talent_req`) scoped to the dimension group | — |
| `placements` | Count of canonical `Placement` per dimension group | — |
| `ghosting` | Count of canonical `Ghosting` per dimension group | — |
| `rejected` | Count of canonical `Rejected` per dimension group | — |
| `placement_rate` | `placements / total_applications × 100` | Candidate Applications (per group) |
| `ghosting_rate` | `ghosting / total_applications × 100` | Candidate Applications (per group) |
| `rejection_rate` | `rejected / total_applications × 100` | Candidate Applications (per group) |
| `fulfillment_rate` | `placements / requested_headcount × 100` | Requested Headcount (per group) |

### Join strategy

- `industry_sector` is joined from `company.csv` via `id_company` in `df_selection`.
- `working_arrangement` is joined from `df_request` via `id_talent_req`.
- `study_program` and `placement_type` are columns already present in `df_selection`.
- Missing dimension values are mapped to `"Unknown"`.

## Current integration notes

- `as_of_date` is the maximum relevant date across the six cleaned tables.
- Source outcomes are normalized to `Placement`, `Rejected`, `Ghosting`, or
  `On Progress`; the mapping remains conditional on the upstream audit.
- Request action labels are `Belum Dikirim`, `Kurang Kandidat`,
  `Belum Terpenuhi`, `Terpenuhi`, and `Closed`.
- Semantic relevance ranking uses precomputed cosine similarity scores
  from Qwen3-Embedding-0.6B. Scores are relevance indicators (0–1),
  not acceptance probabilities.
