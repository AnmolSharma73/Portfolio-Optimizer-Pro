"""
visualization/styles.py — Premium dark Plotly theme for Portfolio Optimizer.

Provides:
* ``COLORS``            – colour palette dict (mirrors config/settings.py).
* ``GRADIENT_COLORS``   – 10-colour gradient list for multi-series charts.
* ``CHART_TEMPLATE``    – Full Plotly-compatible template dict.
* ``get_chart_layout()``– Convenience helper that returns a layout dict.
* ``format_hover_template()`` – Build consistent hover HTML.

**Note**: colours are duplicated here (rather than imported from
``config.settings``) to avoid circular-import issues when the
visualisation package is loaded before the config package.
"""

from __future__ import annotations

from typing import List, Tuple

import plotly.graph_objects as go
import plotly.io as pio

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Colour constants (kept in sync with config/settings.py)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLORS: dict[str, str] = {
    "primary":    "#6C63FF",
    "secondary":  "#00D2FF",
    "accent":     "#FFD700",
    "success":    "#00E396",
    "danger":     "#FF4560",
    "warning":    "#FEB019",
    "info":       "#008FFB",
    "background": "#0E1117",
    "card":       "#1A1F2E",
    "text":       "#E0E0E0",
    "text_muted": "#8892A0",
}

GRADIENT_COLORS: list[str] = [
    "#6C63FF",  # Purple
    "#7B6FFF",  # Light purple
    "#5A8DFF",  # Purple-blue
    "#3CA5FF",  # Sky blue
    "#00BCD4",  # Teal
    "#00D2FF",  # Cyan
    "#26C6DA",  # Light teal
    "#00E396",  # Emerald
    "#FEB019",  # Amber
    "#FFD700",  # Gold
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Chart template
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_GRID_COLOR = "#252B3B"
_FONT_FAMILY = "Inter, sans-serif"

CHART_TEMPLATE: dict = {
    "layout": {
        "paper_bgcolor": COLORS["background"],
        "plot_bgcolor":  COLORS["card"],
        "font": {
            "family": _FONT_FAMILY,
            "color":  COLORS["text"],
            "size":   13,
        },
        "title": {
            "font": {
                "size":   18,
                "color":  COLORS["text"],
                "family": _FONT_FAMILY,
            },
            "x":    0.5,
            "xanchor": "center",
        },
        "xaxis": {
            "gridcolor":     _GRID_COLOR,
            "gridwidth":     0.5,
            "linecolor":     _GRID_COLOR,
            "zerolinecolor": _GRID_COLOR,
            "title_font":    {"size": 13},
            "tickfont":      {"size": 11},
        },
        "yaxis": {
            "gridcolor":     _GRID_COLOR,
            "gridwidth":     0.5,
            "linecolor":     _GRID_COLOR,
            "zerolinecolor": _GRID_COLOR,
            "title_font":    {"size": 13},
            "tickfont":      {"size": 11},
        },
        "colorway": GRADIENT_COLORS,
        "legend": {
            "orientation": "h",
            "yanchor":     "top",
            "y":           -0.15,
            "xanchor":     "center",
            "x":           0.5,
            "bgcolor":     "rgba(0,0,0,0)",
            "font":        {"size": 12},
        },
        "margin": {"l": 60, "r": 30, "t": 60, "b": 60},
        "hoverlabel": {
            "bgcolor":     COLORS["card"],
            "font_size":   13,
            "font_family": _FONT_FAMILY,
            "bordercolor": COLORS["primary"],
        },
    },
}

# Register the template with Plotly so any figure can reference it by name.
pio.templates["portfolio_dark"] = go.layout.Template(
    layout=go.Layout(**CHART_TEMPLATE["layout"]),
)
pio.templates.default = "portfolio_dark"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_chart_layout(
    title: str = "",
    height: int = 500,
    showlegend: bool = True,
) -> dict:
    """Return a layout dict that applies the ``portfolio_dark`` template.

    Parameters
    ----------
    title : str
        Chart title text.
    height : int
        Height of the chart in pixels.
    showlegend : bool
        Whether the legend should be visible.

    Returns
    -------
    dict
        A Plotly-compatible layout dict.
    """
    import streamlit as st
    theme = st.session_state.get("theme", "dark")
    bg_color = "#0E1117" if theme == "dark" else "#F8FAFC"
    card_color = "#1A1F2E" if theme == "dark" else "#FFFFFF"
    text_color = "#E0E0E0" if theme == "dark" else "#0F172A"
    grid_color = "#252B3B" if theme == "dark" else "#E2E8F0"

    layout = {
        "template":   "portfolio_dark",
        "title":      {"text": title} if title else {},
        "height":     height,
        "showlegend": showlegend,
        "paper_bgcolor": bg_color,
        "plot_bgcolor":  card_color,
        "font": {"color": text_color},
    }
    return layout

def apply_dynamic_theme(fig):
    import streamlit as st
    theme = st.session_state.get("theme", "dark")
    bg_color = "#0E1117" if theme == "dark" else "#F8FAFC"
    card_color = "#1A1F2E" if theme == "dark" else "#FFFFFF"
    text_color = "#E0E0E0" if theme == "dark" else "#0F172A"
    grid_color = "rgba(255,255,255,0.06)" if theme == "dark" else "rgba(0,0,0,0.06)"

    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=card_color,
        font=dict(color=text_color),
        legend=dict(font=dict(color=text_color)),
    )
    fig.update_xaxes(gridcolor=grid_color, zerolinecolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color, zerolinecolor=grid_color)
    return fig


def format_hover_template(fields: List[Tuple[str, str]]) -> str:
    """Build a consistently styled Plotly hover template string.

    Parameters
    ----------
    fields : list[tuple[str, str]]
        Each tuple is ``(label, format_string)`` — for example
        ``("Date", "%{x}")``, ``("Value", "%{y:,.2f}")``.

    Returns
    -------
    str
        An HTML hover-template string ending with ``<extra></extra>``.

    Example
    -------
    >>> format_hover_template([("Date", "%{x}"), ("Price", "%{y:$,.2f}")])
    '<b>Date</b>: %{x}<br><b>Price</b>: %{y:$,.2f}<extra></extra>'
    """
    parts = [f"<b>{label}</b>: {fmt}" for label, fmt in fields]
    return "<br>".join(parts) + "<extra></extra>"
