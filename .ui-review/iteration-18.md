# Dashboard UI Review — Iteration 18

## Summary

Chart-scope score: 4.80 / 5  
Critical: 0  
High: 0  
Medium: 2  
Low: 0

## Objective validation

- Project tests: 93 passed.
- Python compile check: passed.
- Browser checks: passed after a clean server restart.
- Screenshots: 15 configured captures produced under `tests/visual/screenshots/iteration-18/`.

## Changes reviewed

- Added shared request labels with request IDs.
- Added complete chronological monthly domains with zero-fill.
- Added explicit business ordering for stages and action labels.
- Added Carbon semantic color maps.
- Corrected Candidate Applications ranking to use `candidate_applications`.
- Replaced the match-score histogram with exact-score bars.
- Replaced the three-record time-to-placement histogram with a dot plot.
- Replaced single-category placement charts with compact insights.

## Remaining findings

- Monthly axes still exposed raw `YYYY-MM` labels in this capture.
- The capture harness needed stronger hydration waiting for deterministic Plotly evidence.

## Next iteration

Format month labels for people and make the visual harness wait for a hydrated Plotly graph.
