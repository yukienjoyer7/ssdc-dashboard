# Dashboard Prototype Specification

The app follows the SSDC 2026 workflow:

```text
overall condition -> request priority -> candidate matching -> selection follow-up -> placement outcomes
```

## Pages

| Page | Decision supported | Primary output |
| --- | --- | --- |
| Executive Overview | What needs attention? | KPI summary, trends, selection distribution, action queue |
| Talent Request Management | Which request should be handled first? | Aging, gap, supply, priority, action table |
| Talent Matching | Which candidates fit a selected request? | Ranked shortlist with explanations |
| Selection Monitoring | Who needs follow-up now? | Stage aging and follow-up queue |
| Placement Performance | Where are outcomes strongest or weakest? | Placement trend and breakdowns |

Global filters are date range, company, study program, request status, and
placement type. Page-specific controls refine the global context without
changing the source tables.

## Prototype status

The app is intentionally executable before final analytical validation. Cards,
tables, and charts are populated from cleaned local CSVs when available. Rules
that still require PM/Data Engineer approval are marked `Prototype logic` in the
interface and documented in `docs/decisions.md`.
