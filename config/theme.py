import streamlit as st


FONT_FAMILY = "'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif"

TYPE_SCALE = {
    "page_title": "2rem",
    "section_title": "1.125rem",
    "subsection_title": "1rem",
    "body": "1rem",
    "page_description": "0.9375rem",
    "body_compact": "0.875rem",
    "label": "0.8125rem",
    "helper": "0.75rem",
    "kpi_primary": "2rem",
    "kpi_compact": "1.5rem",
    "chart_title": "1rem",
}

TYPE_WEIGHTS = {
    "regular": 400,
    "medium": 500,
    "semibold": 600,
}

PLOTLY_FONT_SIZES = {
    "body": 13,
    "axis": 12,
    "legend": 12,
    "tooltip": 13,
}

TEXT_COLORS = {
    "primary": "#161616",
    "secondary": "#525252",
    "helper": "#6f6f6f",
}

SURFACE_COLORS = {
    "background": "#ffffff",
    "layer_01": "#f4f4f4",
    "layer_02": "#ffffff",
    "layer_hover": "#e8e8e8",
    "layer_selected": "#e0e0e0",
    "highlight": "#d0e2ff",
    "border_subtle": "#e0e0e0",
    "border_strong": "#c6c6c6",
    "interactive": "#0f62fe",
}

SPACING = {
    "01": "0.125rem",
    "02": "0.25rem",
    "03": "0.5rem",
    "04": "0.75rem",
    "05": "1rem",
    "06": "1.5rem",
    "07": "2rem",
    "08": "2.5rem",
    "09": "3rem",
}

DASHBOARD_LAYOUT = {
    "content_max_width": "1400px",
    "sidebar_width": "16rem",
    "sidebar_collapsed_width": "3rem",
    "gutter_wide": "2rem",
    "gutter_medium": "1.5rem",
    "gutter_narrow": "1rem",
}

CHART_CATEGORICAL = [
    "#4589ff",
    "#009d9a",
    "#a56eff",
    "#1192e8",
    "#24a148",
    "#ee5396",
    "#ff832b",
    "#8d8d8d",
]

CHART_SEQUENTIAL_BLUE = [
    "#edf5ff",
    "#d0e2ff",
    "#a6c8ff",
    "#78a9ff",
    "#4589ff",
    "#0f62fe",
    "#0043ce",
    "#002d9c",
    "#001d6c",
    "#001141",
]

# Lighter tint tier for large chart fills (bars/lines/areas), kept distinct
# from CARBON_STATUS_COLORS["info"] (full-strength brand blue used for
# links/status/UI chrome) on purpose: saturated color across a whole chart
# canvas causes eye fatigue that a small UI accent doesn't.
CHART_PRIMARY = CHART_CATEGORICAL[0]

PLACEMENT_TYPE_COLORS = {
    "Magang": CHART_CATEGORICAL[0],
    "Part-time": CHART_CATEGORICAL[1],
    "Full-time": CHART_CATEGORICAL[2],
}

EXECUTIVE_OVERVIEW_SERIES_COLORS = {
    "Talent requests": CHART_CATEGORICAL[0],
    "Placements": CHART_CATEGORICAL[1],
}

CARBON_STATUS_COLORS = {
    "info": "#0f62fe",
    "success": "#198038",
    "warning": "#f1c21b",
    "error": "#da1e28",
}

ACTION_LABEL_COLORS = {
    # Kurang Kandidat is an active shortfall, not a neutral info state -- it
    # gets the deeper amber tier so the ramp reads Belum Dikirim (mild) <
    # Kurang Kandidat (deeper concern) < Belum Terpenuhi (critical), instead
    # of reusing "info" blue (the same hue as a default, unremarkable series).
    "Belum Dikirim": CARBON_STATUS_COLORS["warning"],
    "Kurang Kandidat": CHART_CATEGORICAL[6],
    "Belum Terpenuhi": CARBON_STATUS_COLORS["error"],
    "Terpenuhi": CARBON_STATUS_COLORS["success"],
    "Closed": TEXT_COLORS["secondary"],
}

ACTION_LABEL_ORDER = [
    "Belum Dikirim",
    "Kurang Kandidat",
    "Belum Terpenuhi",
    "Terpenuhi",
    "Closed",
]

SELECTION_STAGE_ORDER = [
    "Submitted",
    "Interview User",
    "FU 1",
    "FU 2",
    "FU 3",
    "Finish",
    "Placement",
    "Ghosting",
    "Rejected",
]

SELECTION_STAGE_COLORS = {
    "Submitted": CARBON_STATUS_COLORS["info"],
    "Interview User": "#8a3ffc",
    # FU 1-3 step through a light-to-dark teal ramp so escalating follow-up
    # urgency is visible, instead of three identical bars.
    "FU 1": "#82cfcd",
    "FU 2": "#009d9a",
    "FU 3": "#005d5d",
    "Finish": TEXT_COLORS["secondary"],
    "Placement": CARBON_STATUS_COLORS["success"],
    "Ghosting": CARBON_STATUS_COLORS["error"],
    # Rejected is a distinct negative outcome from Ghosting, not a neutral
    # one -- flat gray understated it next to Ghosting's alarm red.
    "Rejected": CHART_CATEGORICAL[5],
}

RECOMMENDATION_COLORS = {
    "Strong match": CARBON_STATUS_COLORS["success"],
    "Potential match": CARBON_STATUS_COLORS["info"],
    "Review": CARBON_STATUS_COLORS["warning"],
}


def _typography_css_tokens() -> str:
    surface_token_names = {
        "background": "surface-background",
        "layer_01": "surface-layer-01",
        "layer_02": "surface-layer-02",
        "layer_hover": "surface-layer-hover",
        "layer_selected": "surface-layer-selected",
        "highlight": "surface-highlight",
        "border_subtle": "border-subtle",
        "border_strong": "border-strong",
        "interactive": "interactive",
    }
    tokens = {
        "font-family": FONT_FAMILY,
        **{f"type-{name.replace('_', '-')}": value for name, value in TYPE_SCALE.items()},
        **{f"weight-{name}": value for name, value in TYPE_WEIGHTS.items()},
        **{f"text-{name}": value for name, value in TEXT_COLORS.items()},
        **{
            token_name: SURFACE_COLORS[color_name]
            for color_name, token_name in surface_token_names.items()
        },
    }
    app_tokens = [f"            --app-{name}: {value};" for name, value in tokens.items()]
    spacing_tokens = [
        f"            --cds-spacing-{name}: {value};"
        for name, value in SPACING.items()
    ]
    layout_tokens = [
        f"            --dashboard-{name.replace('_', '-')}: {value};"
        for name, value in DASHBOARD_LAYOUT.items()
    ]
    return "\n".join([*app_tokens, *spacing_tokens, *layout_tokens])


def spacing_px(token: str) -> int:
    return round(float(SPACING[token].removesuffix("rem")) * 16)


def inject_theme() -> None:
    typography_tokens = _typography_css_tokens()
    st.markdown(
        "<style>\n"
        "        :root {\n"
        "            color-scheme: light;\n"
        f"{typography_tokens}\n"
        "        }\n"
        """
        [data-testid="stHeader"], [data-testid="stDecoration"],
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: var(--app-surface-layer-01);
        }
        [data-testid="stMain"] {
            box-sizing: border-box;
            padding-inline-start: var(--dashboard-sidebar-width);
        }
        body:has([data-ssdc-sidebar-collapsed]) [data-testid="stMain"] {
            padding-inline-start: var(--dashboard-sidebar-collapsed-width);
        }
        @media (max-width: 48rem) {
            body:has([data-ssdc-sidebar-collapsed]) [data-testid="stMain"] {
                padding-inline-start: 0;
            }
        }
        [data-testid="stMainBlockContainer"], .block-container {
            box-sizing: border-box;
            width: 100%;
            max-width: var(--dashboard-content-max-width);
            margin-inline: auto;
            padding: calc(3rem + var(--cds-spacing-06))
                var(--dashboard-gutter-wide)
                var(--cds-spacing-09);
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            font-family: var(--app-font-family);
        }
        .cds-page-header {
            max-width: 52rem;
            margin: 0;
            min-width: 0;
        }
        .cds-kicker {
            margin: 0 0 var(--cds-spacing-02);
            color: var(--app-text-secondary);
            font-size: var(--app-type-helper);
            font-weight: var(--app-weight-semibold);
            letter-spacing: 0.06em;
            line-height: 1rem;
            text-transform: uppercase;
        }
        .cds-page-title {
            margin: 0;
            color: var(--app-text-primary);
            font-size: clamp(1.75rem, 2vw, var(--app-type-page-title));
            font-weight: var(--app-weight-semibold);
            letter-spacing: -0.02em;
            line-height: 1.2;
        }
        .cds-page-description {
            max-width: 52rem;
            margin: var(--cds-spacing-03) 0 0;
            color: var(--app-text-secondary);
            font-size: var(--app-type-page-description);
            font-weight: var(--app-weight-regular);
            line-height: 1.5;
        }
        .carbon-source {
            border-left: 3px solid var(--app-interactive);
            background: var(--app-surface-background);
            color: var(--app-text-primary);
            padding: 0.75rem 1rem;
            margin: 0.5rem 0 1.5rem;
        }
        .carbon-source-warning { border-left-color: #f1c21b; }
        .cds-section-header {
            max-width: 56rem;
            margin: 0;
        }
        .cds-section-heading {
            margin: 0;
            color: var(--app-text-primary);
            font-size: var(--app-type-section-title);
            font-weight: var(--app-weight-semibold);
            line-height: 1.35;
        }
        .cds-section-note {
            margin: var(--cds-spacing-02) 0 0;
            color: var(--app-text-secondary);
            font-size: var(--app-type-label);
            font-weight: var(--app-weight-regular);
            line-height: 1.45;
        }
        [class*="st-key-cds-control-group-"] {
            gap: var(--cds-spacing-04);
            margin-block-end: var(--cds-spacing-03);
            padding-block: var(--cds-spacing-03);
            border-block: 1px solid var(--app-border-subtle);
        }
        .cds-control-group__label {
            display: block;
            margin: 0;
            color: var(--app-text-secondary);
            font-size: var(--app-type-label);
            font-weight: var(--app-weight-semibold);
            letter-spacing: 0.02em;
            line-height: 1rem;
        }
        .carbon-chart-title {
            color: var(--app-text-primary);
            font-size: var(--app-type-chart-title);
            font-weight: var(--app-weight-medium);
            line-height: 1.375rem;
            margin: 0;
        }
        [class*="st-key-cds-chart-surface-"] {
            min-height: 24rem;
            margin-block-end: var(--cds-spacing-03);
            background: var(--app-surface-background);
            border: 1px solid var(--app-border-subtle) !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: var(--cds-spacing-05);
            transition: border-color 110ms ease-out;
        }
        [class*="st-key-cds-chart-surface-compact-"] {
            min-height: 18rem;
        }
        [class*="st-key-cds-chart-surface-"]:hover {
            border-color: var(--app-border-strong) !important;
        }
        .cds-chart-surface__header {
            margin: 0 0 var(--cds-spacing-04);
            padding: 0;
        }
        [class*="st-key-cds-chart-surface-"]
        > [data-testid="stElementContainer"]:has(.cds-chart-surface__header--described) {
            min-height: 3.0625rem !important;
        }
        .cds-chart-surface__title {
            color: var(--app-text-primary);
            font-size: var(--app-type-chart-title);
            font-weight: var(--app-weight-medium);
            line-height: 1.375rem;
            margin: 0 !important;
            padding: 0 !important;
        }
        .cds-chart-surface__description {
            color: var(--app-text-secondary);
            font-size: var(--app-type-label);
            font-weight: var(--app-weight-regular);
            line-height: 1.125rem;
            margin: var(--cds-spacing-02) 0 0;
        }
        .cds-chart-insight {
            display: flex;
            min-height: 10rem;
            flex-direction: column;
            justify-content: center;
            border-left: 3px solid var(--app-interactive);
            padding: var(--cds-spacing-05) var(--cds-spacing-06);
            background: var(--app-surface-layer-01);
        }
        .cds-chart-insight__value {
            color: var(--app-text-primary);
            font-size: 2rem;
            font-weight: var(--app-weight-semibold);
            line-height: 1.1;
        }
        .cds-chart-insight__label,
        .cds-chart-insight__detail {
            margin: var(--cds-spacing-02) 0 0;
            color: var(--app-text-primary);
            font-size: var(--app-type-body-compact);
            line-height: 1.4;
        }
        .cds-chart-insight__detail {
            color: var(--app-text-secondary);
        }
        .cds-candidate-detail {
            background: var(--app-surface-layer-01);
            border: 1px solid var(--app-border-subtle);
            border-radius: 0;
            padding: var(--cds-spacing-05);
            margin-top: var(--cds-spacing-04);
        }
        .cds-candidate-detail__header {
            margin-bottom: var(--cds-spacing-04);
        }
        .cds-candidate-detail__name {
            font-size: var(--app-type-subsection-title);
            font-weight: var(--app-weight-semibold);
            color: var(--app-text-primary);
            margin: 0 0 var(--cds-spacing-02) 0;
        }
        .cds-candidate-detail__program {
            font-size: var(--app-type-label);
            color: var(--app-text-secondary);
            margin: 0;
        }
        .cds-candidate-detail__explanation {
            font-size: var(--app-type-body-compact);
            color: var(--app-text-primary);
            line-height: 1.5;
            margin: var(--cds-spacing-04) 0;
            padding: var(--cds-spacing-03);
            background: var(--app-surface-background);
            border-left: 3px solid var(--app-interactive);
        }
        .cds-candidate-detail__fields {
            display: grid;
            gap: var(--cds-spacing-03);
        }
        .cds-candidate-detail__field {
            display: flex;
            flex-direction: column;
            gap: var(--cds-spacing-01);
        }
        .cds-candidate-detail__label {
            font-size: var(--app-type-helper);
            font-weight: var(--app-weight-medium);
            color: var(--app-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .cds-candidate-detail__value {
            font-size: var(--app-type-body-compact);
            color: var(--app-text-primary);
            line-height: 1.4;
        }
        .cds-candidate-detail__tag {
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 0;
            font-size: var(--app-type-helper);
            font-weight: var(--app-weight-medium);
            line-height: 1.4;
        }
        .cds-candidate-detail__tag--success {
            background: #defbe6;
            color: #0e6027;
        }
        .cds-candidate-detail__tag--warning {
            background: #fff8e6;
            color: #8e6a00;
        }
        .cds-candidate-detail__tag--info {
            background: #e5f6ff;
            color: #0043ce;
        }
        .cds-candidate-detail__skills {
            font-size: var(--app-type-body-compact);
            color: var(--app-text-primary);
            line-height: 1.5;
            word-break: break-word;
        }
        .cds-candidate-detail__caution {
            margin-top: var(--cds-spacing-03);
            padding: var(--cds-spacing-03);
            background: #fff8e6;
            border-left: 3px solid #f1c21b;
            font-size: var(--app-type-body-compact);
            color: #8e6a00;
            line-height: 1.4;
        }
        @media (max-width: 75rem) {
            [class*="st-key-cds-analytical-grid-"] [data-testid="stHorizontalBlock"] {
                flex-direction: column;
            }
            [class*="st-key-cds-analytical-grid-"] [data-testid="stColumn"] {
                flex: 1 1 auto !important;
                width: 100% !important;
                min-width: 100% !important;
            }
        }
        @media (max-width: 56.25rem) {
            [data-testid="stMainBlockContainer"], .block-container {
                padding-inline: var(--dashboard-gutter-medium);
            }
        }
        @media (max-width: 48rem) {
            [data-testid="stMain"] {
                padding-inline-start: 0;
            }
        }
        @media (max-width: 40rem) {
            [data-testid="stMainBlockContainer"], .block-container {
                padding-inline: var(--dashboard-gutter-narrow);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
