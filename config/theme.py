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

CHART_PRIMARY = CHART_CATEGORICAL[0]

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


def _typography_css_tokens() -> str:
    tokens = {
        "font-family": FONT_FAMILY,
        **{f"type-{name.replace('_', '-')}": value for name, value in TYPE_SCALE.items()},
        **{f"weight-{name}": value for name, value in TYPE_WEIGHTS.items()},
        **{f"text-{name}": value for name, value in TEXT_COLORS.items()},
    }
    app_tokens = [f"            --app-{name}: {value};" for name, value in tokens.items()]
    spacing_tokens = [
        f"            --cds-spacing-{name}: {value};"
        for name, value in SPACING.items()
    ]
    return "\n".join([*app_tokens, *spacing_tokens])


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
        [data-testid="stAppViewContainer"] { background: #f4f4f4; }
        .block-container {
            max-width: none;
            padding: calc(3rem + var(--cds-spacing-06)) 2rem var(--cds-spacing-09) 18rem;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            font-family: var(--app-font-family);
        }
        .cds-page-header {
            max-width: 52rem;
            margin: 0;
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
            border-left: 3px solid #0f62fe;
            background: #ffffff;
            color: #161616;
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
            background: #ffffff;
            border-color: #e0e0e0 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: var(--cds-spacing-05);
            transition: border-color 110ms ease-out;
        }
        [class*="st-key-cds-chart-surface-"]:hover {
            border-color: #8d8d8d !important;
        }
        .cds-chart-surface__header {
            margin: 0 0 var(--cds-spacing-04);
        }
        .cds-chart-surface__title {
            color: var(--app-text-primary);
            font-size: var(--app-type-chart-title);
            font-weight: var(--app-weight-medium);
            line-height: 1.375rem;
            margin: 0;
        }
        .cds-chart-surface__description {
            color: var(--app-text-secondary);
            font-size: var(--app-type-label);
            font-weight: var(--app-weight-regular);
            line-height: 1.125rem;
            margin: var(--cds-spacing-02) 0 0;
        }
        @media (max-width: 48rem) {
            .block-container {
                padding: calc(3rem + var(--cds-spacing-06)) var(--cds-spacing-05) var(--cds-spacing-09);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
