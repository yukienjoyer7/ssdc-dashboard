# Dashboard page patterns

The five page archetypes are defined in `components/carbon_ui.py:PAGE_SPECS`: Executive overview, Talent request management, Talent matching, Selection monitoring, and Placement performance. Pages use `app_pages/common.py:start_page` for context/header/status, `components/ui.py` for section/grid helpers, `components/charts.py` for charts, and Carbon tables/feedback for details and states.

Maintain the existing summary → explanation → actionable detail flow. Use `analytical_columns` deliberate `equal`, `main_supporting`, or `supporting_main` proportions. Do not alter page routing or data contracts as a visual change.

