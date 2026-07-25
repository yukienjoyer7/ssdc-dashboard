# Iteration 12 — Carbon identity mapping and sidebar layering

## Overall score

4.66 / 5 carried forward from the last full rubric review. This iteration was a targeted identity and shell-polish change; it was validated across the complete application, but no score inflation is claimed without a fresh full category-by-category reviewer pass.

## Page scores carried forward

| Page | Score |
| --- | ---: |
| Executive overview | 4.41 |
| Talent request management | 4.72 |
| Talent matching | 4.71 |
| Selection monitoring | 4.77 |
| Placement performance | 4.70 |

## Objective validation

- Frontend typecheck and production build: passed.
- Project tests: 93 passed.
- Python compile check: passed.
- Browser checks: 5 configured pages passed.
- Tablet sidebar collapse/reopen: passed.
- Browser console errors: 0.
- Uncaught page errors: 0.
- Horizontal overflow at required browser checks: none detected.
- Screenshots captured for all 5 pages at desktop, laptop, and tablet viewports under `tests/visual/screenshots/iteration-12/`.

## Findings

### Critical / High / Medium

None introduced or observed in this targeted review.

### Low

- The dashboard still uses the text-only `SSDC` wordmark because a production logo is not yet available; this iteration intentionally does not fabricate one.
- The matching navigation entry uses Carbon’s `search` UI icon because the installed Carbon icon set does not expose a `user--search` UI icon. The page header uses the official `user--search` pictogram as mapped.

## Evidence

- The desktop capture shows a distinct white sidebar layer against the gray dashboard canvas, with a subtle right border and no decorative shadow.
- Each sidebar entry now renders a monochrome Carbon UI icon with the existing active-state treatment preserved.
- Each page header renders one official Carbon pictogram in a restrained 56px square container, with an accessible label and no interaction semantics.
- Tablet captures preserve the compact header and responsive navigation behavior.

## Cross-page findings and root causes

The sidebar and page identity were shared-shell concerns, so the change was implemented in `PAGE_SPECS`, the shared shell renderer, and the shared page-header renderer. No page-specific CSS or business-logic changes were made.

## Changes selected

- Added separate `carbon_icon` and `pictogram` fields to the shared page registry while preserving Streamlit’s existing Material icon field for route registration.
- Added official `@carbon/icons` and `@carbon/pictograms` assets to the packaged Carbon component.
- Added Carbon icon rendering to navigation links using the supported `title-icon` slot.
- Added the `pictogram` component view and shared page-header placement.
- Changed the sidebar to use the Carbon surface layer token distinct from the main dashboard canvas.
- Added mapping and compiled-asset regression tests.

## Regression risks

- Reusing the existing `PageSpec.icon` field for Carbon names would break Streamlit route registration; this was caught by the runtime check and corrected by separating `carbon_icon`.
- Rebuilding the packaged component changes its hashed JavaScript asset; the server was restarted after the rebuild and the browser suite was rerun.

## Recommended next iteration

Run a fresh full reviewer pass after the identity changes. If the sidebar still needs a stronger product identity, add a real approved logo asset rather than extending the pictogram treatment into a logo.
