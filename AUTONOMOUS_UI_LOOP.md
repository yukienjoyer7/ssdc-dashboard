# Autonomous UI loop execution prompt

This is a future execution prompt. Do not use it for the infrastructure-preparation task that created it.

Use `dashboard-ui-reviewer` to decide what is wrong and `carbon-streamlit` to decide how to implement fixes. Preserve KPI formulas, aggregations, data loading, contracts, filtering, session state, routing, chart/table data, downloads, and mock fallback behavior.

Before starting, read the latest `.ui-review/` report and confirm the repository’s branch/status. Never switch branches or rewrite history.

For iteration 1..8:

1. Start or verify Streamlit.
2. Run objective UI checks.
3. Capture every required page at every viewport.
4. Review using `dashboard-ui-reviewer`.
5. Write `.ui-review/iteration-XX.md`.
6. Rank findings by severity.
7. Identify cross-page/shared root causes.
8. Select the smallest set of highest-impact fixes.
9. Implement using `carbon-streamlit`.
10. Run project tests.
11. Run objective UI checks again.
12. Re-capture screenshots.
13. Re-score.
14. Evaluate convergence.

Stop when all convergence criteria are met: every page ≥4.0 overall; no page category <3.5; no Critical/High findings; browser checks and project tests pass; no overflow or application-caused console errors; and two consecutive reviews have no new High finding. Do not continue changing the UI after convergence. Iteration 8 is a hard stop; if convergence is not reached, write `.ui-review/final-report.md`, explain blockers, and stop.

Use:

```bash
uv run python tests/visual/check_ui.py
uv run python tests/visual/capture_pages.py
uv run pytest
uv run python -m compileall app.py config components data services app_pages tests/visual
```

Every iteration must review the complete application. Prefer shared-system corrections, re-test after coherent batches, and document regression risks. Do not begin open-ended redesign or invent selectors merely to make checks pass.

