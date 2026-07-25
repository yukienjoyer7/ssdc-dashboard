# ssdc-carbon-components

Carbon Design System components for the SSDC Streamlit dashboard

## Installation instructions

```sh
uv pip install ssdc-carbon-components
```

### Development install (editable)

When developing this component locally, install it in editable mode so Streamlit picks up code changes without rebuilding a wheel. Run this from the directory that contains `pyproject.toml`:

```sh
uv pip install -e . --force-reinstall
```

## Usage instructions

```python
from ssdc_carbon_components import render_surface

action = render_surface(
    "kpis",
    {"items": [{"label": "Requests", "value": "128"}]},
    key="preview-kpis",
)
```

The package exposes one typed surface renderer. The dashboard supplies a view
name and serializable data; user interactions are returned as an action
dictionary through the Streamlit Components v2 trigger channel.

## Build a wheel

To package this component for distribution:

1. Build the frontend assets (from `ssdc_carbon_components/frontend`):

   ```sh
   npm i
   npm run build
   ```

2. Build the Python wheel using UV (from the project root):
   ```sh
   uv build
   ```

This will create a `dist/` directory containing your wheel. The wheel includes the compiled frontend from `ssdc_carbon_components/frontend/build`.

### Requirements

- Python >= 3.10
- Node.js >= 24 (LTS)

### Expected output

- `dist/ssdc_carbon_components-0.0.1-py3-none-any.whl`
- If you run `uv run --with build python -m build` (without `--wheel`), you’ll also get an sdist: `dist/ssdc-carbon-components-0.0.1.tar.gz`
