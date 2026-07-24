# Carbon Streamlit implementation

This skill decides how to implement fixes identified by `dashboard-ui-reviewer`. It is repository-specific guidance, not the quality authority. Inspect the existing shared components and tokens before editing. Preserve KPI formulas, aggregations, data loading, source contracts, filters, session state, routing, chart/table data, downloads, and mock fallback behavior.

## Implementation workflow

1. Read the latest reviewer report and select only the highest-impact Critical/High findings.
2. Trace each finding to its root cause; prefer shared components, tokens, CSS, chart factories, and layout helpers.
3. Make the smallest coherent batch of changes.
4. Use the actual Carbon component package and `config/theme.py` tokens where applicable.
5. Run project tests, compile checks, objective UI checks, and a complete recapture.
6. Re-review every affected page and record regressions or unresolved findings.

Do not add gradients, glassmorphism, decorative shadows, large radii, arbitrary accent colors, colorful KPI backgrounds, decorative badges/icons/animation, unjustified charts, or sections added to fill whitespace. CSS is shared by default; page-specific CSS requires a documented page-specific requirement.

See the references for the repository map, page patterns, chart rules, CSS policy, UX checklist, and validation checklist.

