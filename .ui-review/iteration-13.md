# Iteration 13 — Carbon top bar and sidebar collapse

## Overall score

4.66 / 5 carried forward from the last full rubric review. This iteration adds shell utility and responsive behavior; a fresh full reviewer pass is still required before changing the rubric score.

## Objective validation

- Frontend typecheck and production build: passed.
- Project tests: 93 passed.
- Python compile check: passed.
- Browser checks: 5 configured pages passed.
- Desktop sidebar collapse/reopen: passed.
- Tablet sidebar collapse/reopen: passed.
- Collapsed desktop main gutter: reduced from 256px to 0px.
- Browser console errors: 0.
- Uncaught page errors: 0.
- Horizontal overflow at required browser checks: none detected.
- Screenshots captured for all 5 pages at desktop, laptop, and tablet viewports under `tests/visual/screenshots/iteration-13/`.

## Findings

### Critical / High / Medium

None introduced or observed.

### Low

- Help is intentionally a disabled placeholder labeled “Help coming soon”; it has no project-context content yet.
- The dashboard still uses the text-only `SSDC` wordmark because no approved production logo is available.

## Evidence

- Desktop capture shows a 48px Carbon header with `SSDC`, `Talent Intelligence`, `Prototype data`, and a quiet Help affordance.
- Desktop toggle validation confirms the sidebar can collapse and the main content expands into the released gutter.
- Tablet capture preserves the compact menu, hides secondary header context, and supports open/close behavior.
- The sidebar’s distinct white Carbon layer and mapped Carbon navigation icons remain intact.

## Cross-page findings and root causes

The top bar and collapse behavior are shared-shell concerns. The implementation is centralized in the Carbon shell, packaged component CSS, and shared theme layout state; no page-specific layout or business logic changed.

## Changes selected

- Added a shared Carbon top bar with product identity and prototype/local data context.
- Added a disabled Help placeholder with accessible labeling and a Carbon Help icon.
- Enabled the existing sidebar control at desktop widths and retained tablet behavior.
- Added explicit shared layout state so collapsing the shell removes the main content gutter.
- Updated objective checks to validate desktop and tablet collapse/reopen.

## Regression risks

- Carbon fixed side-nav mode synchronizes the menu button itself; the handler now defers to Carbon’s final active state to avoid double toggles.
- The component is isolated from the Streamlit theme, so the shell exposes a host attribute for the parent layout to respond to; cleanup removes that attribute on unmount.

## Recommended next iteration

Review the shell at the next full rubric pass. Keep Help disabled until project context, documentation, or support behavior is defined.
