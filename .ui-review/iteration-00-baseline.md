# Dashboard UI Review — Iteration 00

## Summary

Overall score: 3.84 / 5  
Critical: 0  
High: 2  
Medium: 4  
Low: 0

Evidence reviewed: 15 deterministic screenshots in `tests/visual/screenshots/` (five pages at desktop 1440×1000, laptop 1280×900, and tablet 768×1024), plus the objective browser run against Streamlit on port 8502. Scores are baseline observations only; no recommendations below were implemented during setup.

## Objective Validation

| Check | Result | Evidence |
|---|---|---|
| Application boot | PASS | Streamlit 1.59.2 served the app at `http://127.0.0.1:8502` |
| Navigation | PASS | 5 configured destinations reached via the visible shell at desktop viewport |
| Filters | PARTIAL | Filter surface is visible; apply/reset automation is not claimed because the custom component has no stable public selector contract |
| Console | PASS | 0 console errors and 0 uncaught page errors in the shell-based objective run |
| Horizontal overflow | PASS | Page and `stMain` scroll-width checks passed for all five pages at the objective desktop viewport |
| Tests | PASS | 91 existing tests passed |
| Screenshot capture | PASS | 15/15 deterministic screenshots produced |

Direct page routes are used for captures so tablet screenshots can render the actual page. The objective check uses the desktop shell route to avoid harmless Streamlit route/asset 404 noise; this is documented in `tests/visual/README.md`.

## Page Scores

| Page | Score | Main issue |
|---|---:|---|
| Executive overview | 3.90 | Supporting KPI row competes with the primary outcome row; charts begin below the first viewport |
| Talent request management | 3.82 | Dense control stack and chart/table work area reduce early analytical focus |
| Talent matching | 3.61 | Tablet KPI values lose label/value separation and create large unused vertical gaps |
| Selection monitoring | 3.93 | Eight KPI tiles dilute the follow-up queue’s action hierarchy |
| Placement performance | 4.00 | Clear outcome flow, but tablet secondary chart is below the first viewport |

## Category Scores

Scores are ordered by the rubric: Information hierarchy, Analytical usefulness, Layout & alignment, Information density, Visual consistency, Data visualization quality, Interaction clarity, Typography & readability, Responsive behavior, Accessibility.

| Page | Category scores | Evidence summary |
|---|---|---|
| Executive overview | 3.8, 4.0, 4.0, 3.8, 4.0, 3.8, 3.8, 4.2, 3.8, 4.0 | Clear question and primary outcomes; the secondary four-tile row has equal visual weight; desktop grid aligns; charts begin below the first viewport; tablet wraps cleanly. |
| Talent request management | 3.8, 4.0, 3.8, 3.5, 4.0, 3.8, 3.6, 4.0, 3.8, 4.0 | Action question is clear and charts are decision-oriented; filter controls occupy substantial space before KPIs; six equal KPI tiles and dense chart labels compete with the request queue. |
| Talent matching | 3.4, 3.8, 3.4, 3.0, 3.8, 3.5, 3.4, 3.9, 2.5, 4.0 | Request context and shortlist intent are clear at desktop; tablet shows `CompanyMeridian Goods`, `PositionData Analyst`, and `Requested headcount5` with large intervening gaps; desktop cards and alert are consistent. |
| Selection monitoring | 3.8, 4.0, 4.0, 3.8, 4.0, 3.8, 3.8, 4.1, 4.0, 4.0 | Follow-up question is explicit and filters are understandable; eight KPI tiles spread attention; charts and action-table intent follow coherently; tablet KPI grid remains readable. |
| Placement performance | 4.0, 4.1, 4.1, 4.0, 4.1, 4.0, 3.9, 4.2, 4.0, 4.0 | Strong summary-to-outcome flow, restrained surfaces, stable chart color, and readable tablet wrapping; trend and company breakdown are useful but only one secondary chart is visible early on tablet. |

No page category is below 3.5 except Talent Matching’s responsive, information-density, layout, hierarchy, and interaction scores, all tied to the same tablet KPI rendering issue.

## Critical Findings

None observed. No runtime failure, broken destination, misleading metric, or severe page-wide corruption was found in this dry run.

## High Priority Findings

### H-01 — Talent Matching KPI context collapses at tablet width

Page: Talent Matching  
Viewport: tablet 768×1024  
Evidence: `talent-matching__tablet.png` renders the KPI content as `CompanyMeridian Goods`, `PositionData Analyst`, and `Requested headcount5`, with very large vertical gaps between rows. The desktop version presents the same values as three deliberate tiles.  
Why it matters: The selected request context is a prerequisite for interpreting the candidate shortlist; label/value separation is materially degraded at the required tablet viewport.  
Likely root cause: Responsive CSS or the shared KPI/custom-component layout at the tablet breakpoint.  
Recommended change: Fix the shared KPI responsive layout so labels and values retain a clear relationship and compact row/column rhythm at 768px; re-review all pages using the same component.  
Affected shared system: Carbon KPI component and responsive theme CSS.

### H-02 — Tablet shell has no obvious reopen affordance

Pages: All five tablet captures  
Viewport: tablet 768×1024  
Evidence: Each tablet screenshot shows a compact top bar with `SSDC` and an `×` control, while the page navigation is not visible; no persistent menu/reopen affordance is apparent in the captured state.  
Why it matters: Page switching is a primary dashboard task, and a user who closes the compact shell may not know how to reopen it.  
Likely root cause: Custom Carbon shell responsive state and trigger visibility.  
Recommended change: Make the collapsed-shell toggle explicit, labeled or iconically conventional, and keyboard/focus discoverable at tablet width; validate collapse/reopen behavior rather than styling around it.  
Affected shared system: `render_shell` and the packaged Carbon shell component.

## Medium Findings

### M-01 — Supporting KPI rows compete with primary outcomes

Pages: Executive overview and Selection monitoring  
Evidence: Executive Overview gives the four secondary pipeline metrics the same tile size and surface treatment as the four primary outcomes; Selection Monitoring presents eight same-weight KPI tiles before the risk charts.  
Why it matters: The page question and action path are less immediate when supporting counts have equal prominence.  
Likely root cause: Shared KPI row variants and page-level grouping choices.  
Recommended change: Use the existing primary/compact KPI variants or quieter supporting treatment while preserving values.

### M-02 — Control stacks consume early analytical space

Pages: Talent Request Management and Talent Matching  
Evidence: At desktop, multiple filters/threshold controls appear before the main workload/shortlist detail; the tablet versions push meaningful detail below the first viewport.  
Why it matters: The user’s analytical question is delayed by configuration controls.  
Likely root cause: Page layout order and control grouping, not data logic.  
Recommended change: Review progressive disclosure and keep the selected state visible while making secondary thresholds quieter or collapsible.

### M-03 — Prototype/status metadata is repeated at high-salience locations

Pages: Executive overview, Talent Matching, and Placement Performance  
Evidence: `Prototype data`, `Provisional KPI logic`, record freshness, and `Data details` are repeated directly beneath page headers.  
Why it matters: Provenance is important, but repeated badges compete with the executive reading path and contribute to visual noise.  
Likely root cause: Shared data-status surface and page-header placement.  
Recommended change: Preserve access to provenance but subordinate it through spacing, grouping, or progressive disclosure.

### M-04 — Chart/table detail is frequently below the first viewport

Pages: Executive overview, Selection monitoring, and Placement Performance  
Evidence: Desktop captures show chart modules beginning near the bottom of the first 1000px; tablet captures show only the first chart or its heading before the viewport ends.  
Why it matters: The dashboard’s explanatory and actionable layers require additional scrolling after the KPI layer.  
Likely root cause: Combined header/status/KPI spacing and fixed chart/module heights.  
Recommended change: Review above-the-fold density and chart heights as a shared layout question; do not add content merely to fill space.

## Cross-Page Findings

- The shell, filter toolbar, data-status metadata, KPI surfaces, and content grid are shared systems and should be investigated before page-specific CSS.
- Carbon-neutral surfaces, zero-radius borders, IBM Plex typography, and blue interactive accents are consistent across pages; preserve this restraint.
- The primary page question is explicit on all five pages and section headings generally follow summary → explanation → detail.
- The tablet shell and responsive KPI layout are the two highest-leverage shared root-cause areas.

## Regression Risks

- Changing shared KPI breakpoints may affect six/eight-tile rows on Talent Request Management and Selection Monitoring.
- Changing shell responsive behavior may affect routing and custom-component session events.
- Reducing status prominence must not remove prototype/provisional data warnings.
- Any chart-height or spacing change must be re-captured across all five pages and all three viewports.

## Recommended Next Iteration

1. Trace and fix the shared tablet KPI layout; re-review every KPI-bearing page.
2. Trace the Carbon shell’s tablet collapsed-state trigger and verify collapse/reopen with a stable interaction contract.
3. Re-run complete tests, objective checks, and all 15 captures before considering the medium hierarchy/spacing findings.

