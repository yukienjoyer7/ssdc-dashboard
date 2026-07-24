# Repository component map

| Dashboard role | Actual implementation | Carbon concept |
|---|---|---|
| Application shell/navigation | `components/carbon_ui.py:render_shell`, `app.py` | UI shell / side navigation |
| Global filters | `components/carbon_ui.py:render_filter_toolbar` | filter toolbar / form controls |
| KPI row | `components/carbon_ui.py:render_kpi_row`, `components/ui.py:render_kpis` | Tile principles |
| Feedback/data status | `components/carbon_ui.py:render_feedback`, `render_data_status_surface` | notification/status |
| Charts | `components/charts.py` | shared Plotly chart factory with Carbon tokens |
| Tables | `components/carbon_ui.py:render_table` | Data Table with server-side pagination |
| Page scaffolding | `app_pages/common.py`, `components/ui.py` | content hierarchy and layout grid |
| Tokens/theme | `config/theme.py`, `.streamlit/config.toml` | Carbon light theme |

