# Review output format

Every report must follow this shape:

```markdown
# Dashboard UI Review — Iteration XX

## Summary
Overall score: X.XX / 5
Critical: N
High: N
Medium: N
Low: N

## Objective Validation
Application boot: PASS/FAIL
Navigation: PASS/FAIL
Filters: PASS/FAIL
Console: PASS/FAIL
Horizontal overflow: PASS/FAIL
Tests: PASS/FAIL

## Page Scores
| Page | Score | Main issue |
|---|---:|---|
| ... | ... | ... |

## Category Scores
...

## Critical Findings
...
## High Priority Findings
### H-01 — Finding title
Page: ...
Viewport: ...
Evidence: ...
Why it matters: ...
Likely root cause: ...
Recommended change: ...
Affected shared system: ...
## Medium Findings
...
## Cross-Page Findings
...
## Regression Risks
...
## Recommended Next Iteration
1. ...
```

