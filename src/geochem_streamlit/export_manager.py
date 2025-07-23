"""
Export Manager for GeoQuick
--------------------------
Provides helpers to export Plotly figures and data while **keeping true vector output**
for SVG and PDF formats (i.e. marker symbols remain vectors rather than being
rasterised). In addition it guarantees **complete PNG snapshots** – even when
your figures contain WebGL traces like `scattergl`.

Strategy
~~~~~~~~
* Convert *any* WebGL trace (whose type ends with "gl") to its standard SVG‑
  friendly counterpart *only at export time*.
* Apply layout tweaks (width, height, margins, fonts) uniformly before export.

This keeps the interactive web‑app fast while ensuring that SVG, PDF *and now
PNG* contain every marker.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Tuple

import plotly.graph_objects as go
import streamlit as st

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─── Utility functions ────────────────────────────────────────────────────────


def _is_cloud_environment() -> bool:
    """Detect Streamlit Cloud / Render / Heroku etc. for limited export modes."""
    import os

    cloud_indicators = {
        "STREAMLIT_SHARING",
        "STREAMLIT_CLOUD",
        "RENDER",
        "HEROKU",
        "REPLIT_DEPLOYMENT",
    }
    return any(key in os.environ for key in cloud_indicators)


class ExportError(Exception):
    """Raised when a requested export fails."""


# ─── Core class ───────────────────────────────────────────────────────────────
class ExportManager:
    """Centralises all export‑related helpers."""

    # Default layout tweaks applied before every export  
    DEFAULT_LAYOUT: dict = {
        "width": 1200,
        "height": 800,
        "margin": dict(l=80, r=120, t=60, b=60),
        "showlegend": False,
        "font_family": "Arial",
        "font_size": 14,
        "font_color": "#000",
    }

    # ── Private helpers ────────────────────────────────────────────────────
    @staticmethod
    def _vectorise_traces(fig: go.Figure) -> go.Figure:
        """Return a *copy* of *fig* with WebGL traces swapped to SVG ones."""
        fig_dict = fig.to_plotly_json()
        for trace in fig_dict.get("data", []):
            t_type: str = trace.get("type", "")
            if t_type.endswith("gl"):
                trace["type"] = t_type[:-2]  # drop the trailing "gl"
        return go.Figure(fig_dict)

    @staticmethod
    def _prepare(fig: go.Figure, cfg: Optional[dict] = None) -> go.Figure:
        """Deep‑copy *fig* and merge in layout settings."""
        new_fig = go.Figure(fig.to_plotly_json())
        layout_cfg = ExportManager.DEFAULT_LAYOUT.copy()
        if cfg:
            layout_cfg.update(cfg)
        new_fig.update_layout(**layout_cfg)
        return new_fig

    # ── Public API ─────────────────────────────────────────────────────────
    @staticmethod
    def export_html(fig: go.Figure, filename: Optional[str] = None,
                    cfg: Optional[dict] = None) -> Tuple[str, str]:
        try:
            fig_out = ExportManager._prepare(fig, cfg)
            if not filename:
                filename = f"geoquick_plot_{datetime.now():%Y%m%d_%H%M%S}.html"
            elif not filename.endswith(".html"):
                filename += ".html"

            html = fig_out.to_html(include_plotlyjs="inline",
                                   config={"displayModeBar": True,
                                           "displaylogo": False,
                                           "modeBarButtonsToRemove": [
                                               "pan2d", "lasso2d"]})
            return html, filename
        except Exception as exc:  # noqa: BLE001
            logger.error("HTML export failed: %s", exc)
            raise ExportError(str(exc)) from exc

    @staticmethod
    def export_png(fig: go.Figure, filename: Optional[str] = None,
                   cfg: Optional[dict] = None) -> Tuple[bytes, str]:
        """Export PNG **with all symbols intact** (no missing WebGL layers)."""
        try:
            # 🆕 Ensure WebGL traces are down‑converted before Kaleido snapshot
            fig_out = ExportManager._vectorise_traces(
                ExportManager._prepare(fig, cfg)
            )
            if not filename:
                filename = f"geoquick_plot_{datetime.now():%Y%m%d_%H%M%S}.png"
            elif not filename.endswith(".png"):
                filename += ".png"
            return fig_out.to_image(format="png", engine="kaleido"), filename
        except Exception as exc:  # noqa: BLE001
            logger.error("PNG export failed: %s", exc)
            raise ExportError(str(exc)) from exc

    @staticmethod
    def export_svg(fig: go.Figure, filename: Optional[str] = None,
                   cfg: Optional[dict] = None) -> Tuple[str, str]:
        try:
            fig_out = ExportManager._vectorise_traces(
                ExportManager._prepare(fig, cfg)
            )
            if not filename:
                filename = f"geoquick_plot_{datetime.now():%Y%m%d_%H%M%S}.svg"
            elif not filename.endswith(".svg"):
                filename += ".svg"

            svg_bytes = fig_out.to_image(format="svg", engine="kaleido")
            svg_str = svg_bytes.decode("utf-8") if isinstance(svg_bytes, bytes) else svg_bytes
            return svg_str, filename
        except Exception as exc:  # noqa: BLE001
            logger.error("SVG export failed: %s", exc)
            raise ExportError(str(exc)) from exc

    @staticmethod
    def export_pdf(fig: go.Figure, filename: Optional[str] = None,
                   cfg: Optional[dict] = None) -> Tuple[bytes, str]:
        try:
            fig_out = ExportManager._vectorise_traces(
                ExportManager._prepare(fig, cfg)
            )
            if not filename:
                filename = f"geoquick_plot_{datetime.now():%Y%m%d_%H%M%S}.pdf"
            elif not filename.endswith(".pdf"):
                filename += ".pdf"

            return (fig_out.to_image(format="pdf", engine="kaleido",
                                     width=fig_out.layout.width,
                                     height=fig_out.layout.height),
                    filename)
        except Exception as exc:  # noqa: BLE001
            logger.error("PDF export failed: %s", exc)
            raise ExportError(str(exc)) from exc


# ─── Streamlit helpers ───────────────────────────────────────────────────────

def render_export_buttons(fig: go.Figure, export_cfg: Optional[dict] = None,
                           key_prefix: str = "export") -> None:
    """Render a trio of download buttons inside Streamlit."""

    st.markdown("### 📥 Export Plot")
    cloud = _is_cloud_environment()

    if cloud:
        # On Streamlit Cloud we only guarantee HTML because Kaleido may be absent
        html, fname = ExportManager.export_html(fig, cfg=export_cfg)
        st.download_button("💾 Save as HTML", html, fname, mime="text/html",
                           use_container_width=True, key=f"{key_prefix}_html")
        st.info("PNG/SVG/PDF exports are disabled in this environment.")
        return

    # Desktop / full Python runtime
    col1, col2, col3 = st.columns(3)

    with col1:
        png_bytes, fname = ExportManager.export_png(fig, cfg=export_cfg)
        st.download_button("🖼 PNG", png_bytes, fname, mime="image/png",
                           use_container_width=True, key=f"{key_prefix}_png")
    with col2:
        svg_str, fname = ExportManager.export_svg(fig, cfg=export_cfg)
        st.download_button("✒️ SVG", svg_str, fname, mime="image/svg+xml",
                           use_container_width=True, key=f"{key_prefix}_svg")
    with col3:
        pdf_bytes, fname = ExportManager.export_pdf(fig, cfg=export_cfg)
        st.download_button("📄 PDF", pdf_bytes, fname, mime="application/pdf",
                           use_container_width=True, key=f"{key_prefix}_pdf")


# ─── UI for export settings ─────────────────────────────────────────────────—

def render_export_settings() -> dict:
    """Collect custom width / height / margin options from the user."""

    with st.expander("🔧 Export Settings"):
        col_w, col_h = st.columns(2)
        with col_w:
            width = st.number_input("Width (px)", 400, 3000, 1200, 100)
        with col_h:
            height = st.number_input("Height (px)", 300, 2000, 800, 100)

        show_legend = st.checkbox("Show legend", value=False)

        with st.expander("Margins"):
            cl, cr, ct, cb = st.columns(4)
            margin = dict(
                l=cl.number_input("Left", 0, 200, 80),
                r=cr.number_input("Right", 0, 200, 120),
                t=ct.number_input("Top", 0, 200, 60),
                b=cb.number_input("Bottom", 0, 200, 60),
            )

    return {"width": width, "height": height, "margin": margin,
            "showlegend": show_legend}