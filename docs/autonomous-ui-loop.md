# Autonomous dashboard UI loop

The bounded loop is:

```text
RUN → CHECK → CAPTURE → REVIEW → PRIORITIZE → ROOT-CAUSE → IMPLEMENT → TEST → RE-CAPTURE → RE-SCORE → CONVERGENCE CHECK
```

`dashboard-ui-reviewer` is the quality authority: it runs the app, validates every page and viewport, scores with evidence, ranks severity, and identifies shared patterns. `carbon-streamlit` is the implementation authority: it traces those findings into existing Carbon components, tokens, CSS, chart factories, and layout helpers while preserving application behavior.

Run the harness with the app running:

```bash
uv run python tests/visual/check_ui.py
uv run python tests/visual/capture_pages.py
```

Run project validation with:

```bash
uv run pytest
uv run python -m compileall app.py config components data services app_pages tests/visual
```

Each review is written as a new `.ui-review/iteration-XX.md`; never overwrite an earlier report. Include objective results, page/category scores with evidence, findings by severity, cross-page root causes, regression risks, and the next batch.

Iteration policy: fix Critical first, then a small number of highest-impact High findings; prefer shared fixes; re-test after each coherent batch; address Medium after higher-severity findings; treat Low as optional. Every iteration re-checks the complete app. If a shared change regresses another page, document and correct/revert the shared change rather than hiding it with a page-specific hack.

Convergence requires all of the following: every page overall score ≥4.0; no page category <3.5; no Critical or High findings; all deterministic browser checks pass; all project tests pass; no required-viewport horizontal overflow; no application-caused browser console errors; and two consecutive reviews with no new High finding. The hard limit is eight iterations. At iteration 8, write the final report even if blocked and stop.

Failure handling: distinguish app failures, deterministic harness failures, environment/browser failures, and review uncertainty. Fix or document only what is in scope. Do not fabricate screenshots, scores, or accessibility compliance. Git safety: preserve the current branch and user changes; do not switch, merge, rebase, reset, push, rewrite history, or modify Git configuration.

