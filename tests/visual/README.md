# Visual/browser harness

The harness uses Python Playwright and the existing `uv` workflow. Start the application in another terminal:

```bash
uv sync
uv run streamlit run app.py --server.headless true
```

Install the browser once after syncing:

```bash
uv run playwright install chromium
```

From the repository root:

```bash
uv run python tests/visual/check_ui.py
uv run python tests/visual/capture_pages.py
```

Checks write a readable summary and exit non-zero on deterministic page-load, visible exception, overflow, console, or uncaught-error failures. Captures are written to `tests/visual/screenshots/` using stable page/viewport names. The manifest is `tests/visual/pages.yaml`.

The five configured routes are the actual `PAGE_SPECS` titles and slugs in `components/carbon_ui.py`. Direct Streamlit routes are attempted first; the scripts fall back to the visible custom shell when a route does not render the expected title. Filter apply/reset and sidebar collapse are reported as limitations because the packaged custom component does not expose a stable public selector contract yet; selectors should be added only when that contract is intentionally established.

Troubleshooting: verify the server is listening at `http://127.0.0.1:8501`, wait for the first Streamlit build to finish, install Chromium, and remove stale screenshots only when deliberately refreshing a run. No remote service or OCR is required.

