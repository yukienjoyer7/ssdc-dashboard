# Validation checklist

- Start the app with `uv run streamlit run app.py`.
- Run `uv run pytest`.
- Run `uv run python -m compileall app.py config components data services app_pages tests/visual`.
- Run `uv run python tests/visual/check_ui.py`.
- Run `uv run python tests/visual/capture_pages.py`.
- Confirm every page and viewport is reviewed.
- Confirm no deterministic browser failure, application console error, or horizontal overflow.
- Re-check all pages after any shared change and record regressions in `.ui-review/`.

