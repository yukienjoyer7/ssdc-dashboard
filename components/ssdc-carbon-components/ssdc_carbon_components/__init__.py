from collections.abc import Mapping
from typing import Any

import streamlit as st


_COMPONENT = st.components.v2.component(
    "ssdc-carbon-components.ssdc_carbon_components",
    js="index-*.js",
    css="index-*.css",
    html='<div class="component-root" aria-live="polite"></div>',
)


def _on_action_change() -> None:
    """Keep the action result available after a frontend-triggered rerun."""


def render_surface(
    view: str,
    data: Mapping[str, Any],
    *,
    key: str,
) -> dict[str, Any] | None:
    """Render a Carbon surface and return its transient user action."""
    result = _COMPONENT(
        key=key,
        data={"view": view, **dict(data)},
        on_action_change=_on_action_change,
    )
    action = getattr(result, "action", None)
    return action if isinstance(action, dict) else None
