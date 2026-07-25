# Dashboard UI Reviewer

This skill is the quality authority for the SSDC dashboard. It decides what is wrong from observable product, dashboard, data-visualization, interaction, responsive, and accessibility evidence. It does not implement fixes.

## Required workflow

For every review iteration:

1. Run or verify the Streamlit app.
2. Run `tests/visual/check_ui.py` and record its output.
3. Capture every page in `tests/visual/pages.yaml` at every configured viewport.
4. Review each page and viewport using the references in this skill.
5. Score every rubric category from 1.0 to 5.0 with evidence.
6. Record findings, rank them by severity, and identify cross-page patterns.
7. Recommend the smallest high-leverage fixes and shared root causes.
8. In improvement mode only, hand the review to `carbon-streamlit` for implementation.
9. Re-run project tests, objective checks, captures, and complete scoring.
10. Check convergence; stop at the documented hard limit.

The baseline setup task may create `iteration-00-baseline.md`, but must not implement its recommendations.

## Review rules

Use `references/review-rubric.md`, `dashboard-principles.md`, `data-viz-review.md`, `interaction-review.md`, `responsive-review.md`, `accessibility-review.md`, `severity-model.md`, `review-output-format.md`, and `reference-calibration.md`. No category score may be unsupported; screenshot inspection is not a formal WCAG audit. Translate aesthetic impressions into observable properties. Prefer shared root-cause fixes whenever an issue appears on two or more pages.

The application’s behavior is a contract: do not recommend changes to KPI formulas, data loading, aggregations, filtering semantics, routing, session state, chart/table data, downloads, or mock-data fallback unless the review identifies a concrete defect and the change is explicitly scoped as a product bug fix.

