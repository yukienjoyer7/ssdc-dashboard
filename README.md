# SSDC Dashboard

Streamlit prototype for the SSDC 2026 dashboard competition.

The application uses the cleaned tables from the sibling `ssdc-data-cleaning`
project when they are available locally. Those tables are intentionally not
committed here because they contain personal information. If the data directory
is unavailable, the app uses a small anonymized deterministic preview and labels
the page accordingly.

## Run locally

From this directory:

```bash
uv sync
uv run streamlit run app.py
```

By default, the app reads:

```text
../ssdc-data-cleaning/data_clean
```

Use `SSDC_DATA_DIR` to point to another cleaned-data directory:

```bash
SSDC_DATA_DIR=/path/to/data_clean uv run streamlit run app.py
```

The five pages follow the intended workflow:

1. Executive Overview
2. Talent Request Management
3. Talent Matching
4. Selection Monitoring
5. Placement Performance

The dashboard KPI cards follow `docs/kpi_dictionary.md`. Semantic matching and
source outcome mappings remain explicitly marked as pending upstream validation.

## Checks

```bash
uv run pytest
uv run python -m compileall app.py config components data services pages
```
