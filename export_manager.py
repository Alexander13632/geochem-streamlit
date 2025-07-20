"""
Export Manager for GeoQuick
Handles export of plots and data in various formats
"""
import io
import logging
from typing import Optional, Tuple
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Custom exception for export-related errors"""
    pass


class ExportManager:
    """Manages export functionality for plots and data"""
    
    # Default export settings
    DEFAULT_PLOT_CONFIG = {
        "width": 1200,
        "height": 800,
        "margin": dict(l=80, r=120, t=60, b=60),
        "showlegend": False
    }
    
    @staticmethod
    def prepare_figure_for_export(fig: go.Figure, 
                                config: Optional[dict] = None) -> go.Figure:
        """
        Prepare figure for export by applying export-specific settings
        
        Args:
            fig: Original plotly figure
            config: Custom configuration dict
            
        Returns:
            Copy of figure with export settings applied
        """
        export_fig = fig.to_dict()  # Deep copy
        export_fig = go.Figure(export_fig)
        
        # Apply configuration
        export_config = ExportManager.DEFAULT_PLOT_CONFIG.copy()
        if config:
            export_config.update(config)
            
        export_fig.update_layout(**export_config)
        return export_fig
    
    @staticmethod
    def export_plot_png(fig: go.Figure, 
                       filename: Optional[str] = None,
                       config: Optional[dict] = None) -> Tuple[bytes, str]:
        """
        Export plot as PNG
        
        Args:
            fig: Plotly figure to export
            filename: Custom filename (optional)
            config: Custom export configuration
            
        Returns:
            Tuple of (image_bytes, filename)
            
        Raises:
            ExportError: If PNG export fails
        """
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.png"
            elif not filename.endswith('.png'):
                filename += '.png'
            
            # Export to PNG
            img_bytes = export_fig.to_image(format="png", engine="kaleido")
            logger.info(f"Successfully exported PNG: {filename}")
            return img_bytes, filename
            
        except Exception as e:
            logger.error(f"PNG export failed: {str(e)}")
            raise ExportError(f"Failed to export PNG: {str(e)}")
    
    @staticmethod
    def export_plot_svg(fig: go.Figure, 
                       filename: Optional[str] = None,
                       config: Optional[dict] = None) -> Tuple[str, str]:
        """
        Export plot as SVG
        
        Args:
            fig: Plotly figure to export
            filename: Custom filename (optional)
            config: Custom export configuration
            
        Returns:
            Tuple of (svg_string, filename)
            
        Raises:
            ExportError: If SVG export fails
        """
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.svg"
            elif not filename.endswith('.svg'):
                filename += '.svg'
            
            # Export to SVG
            svg_string = export_fig.to_image(format="svg", engine="kaleido")
            logger.info(f"Successfully exported SVG: {filename}")
            return svg_string, filename
            
        except Exception as e:
            logger.error(f"SVG export failed: {str(e)}")
            raise ExportError(f"Failed to export SVG: {str(e)}")
    
    @staticmethod
    def export_plot_pdf(fig: go.Figure, 
                       filename: Optional[str] = None,
                       config: Optional[dict] = None) -> Tuple[bytes, str]:
        """
        Export plot as PDF
        
        Args:
            fig: Plotly figure to export
            filename: Custom filename (optional)
            config: Custom export configuration
            
        Returns:
            Tuple of (pdf_bytes, filename)
            
        Raises:
            ExportError: If PDF export fails
        """
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.pdf"
            elif not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Export to PDF
            pdf_bytes = export_fig.to_image(format="pdf", engine="kaleido")
            logger.info(f"Successfully exported PDF: {filename}")
            return pdf_bytes, filename
            
        except Exception as e:
            logger.error(f"PDF export failed: {str(e)}")
            raise ExportError(f"Failed to export PDF: {str(e)}")


def render_export_buttons(fig: go.Figure, 
                         export_config: Optional[dict] = None,
                         key_prefix: str = "export") -> None:
    """
    Render export buttons in Streamlit interface
    
    Args:
        fig: Plotly figure to export
        export_config: Custom export configuration
        key_prefix: Unique prefix for button keys
    """
    st.markdown("### 📥 Export Plot")
    
    col1, col2, col3 = st.columns(3)
    
    # PNG Export
    with col1:
        try:
            img_bytes, filename = ExportManager.export_plot_png(fig, config=export_config)
            st.download_button(
                label="📊 Save PNG",
                data=img_bytes,
                file_name=filename,
                mime="image/png",
                use_container_width=True,
                key=f"{key_prefix}_png"
            )
        except ExportError as e:
            st.error(f"PNG export failed: {str(e)}")
            st.info("💡 Try using the screenshot feature in the plot toolbar")
        except Exception as e:
            logger.error(f"Unexpected PNG export error: {str(e)}")
            st.warning("PNG export temporarily unavailable")
    
    # SVG Export
    with col2:
        try:
            svg_string, filename = ExportManager.export_plot_svg(fig, config=export_config)
            st.download_button(
                label="🎨 Save SVG",
                data=svg_string,
                file_name=filename,
                mime="image/svg+xml",
                use_container_width=True,
                key=f"{key_prefix}_svg"
            )
        except ExportError as e:
            st.error(f"SVG export failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected SVG export error: {str(e)}")
            st.warning("SVG export temporarily unavailable")
    
    # PDF Export
    with col3:
        try:
            pdf_bytes, filename = ExportManager.export_plot_pdf(fig, config=export_config)
            st.download_button(
                label="📄 Save PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
                key=f"{key_prefix}_pdf"
            )
        except ExportError as e:
            st.error(f"PDF export failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected PDF export error: {str(e)}")
            st.warning("PDF export temporarily unavailable")


def render_export_settings() -> dict:
    """
    Render export settings UI and return configuration
    
    Returns:
        Dictionary with export configuration
    """
    with st.expander("🔧 Export Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            width = st.number_input("Width (px)", 
                                  min_value=400, max_value=3000, 
                                  value=1200, step=100)
            height = st.number_input("Height (px)", 
                                   min_value=300, max_value=2000, 
                                   value=800, step=100)
        
        with col2:
            show_legend = st.checkbox("Show legend in export", value=False)
            high_quality = st.checkbox("High quality (slower)", value=True)
        
        # Advanced margins
        with st.expander("Margins", expanded=False):
            col_l, col_r, col_t, col_b = st.columns(4)
            left = col_l.number_input("Left", 20, 200, 80)
            right = col_r.number_input("Right", 20, 200, 120)
            top = col_t.number_input("Top", 20, 200, 60)
            bottom = col_b.number_input("Bottom", 20, 200, 60)
    
    return {
        "width": width,
        "height": height,
        "margin": dict(l=left, r=right, t=top, b=bottom),
        "showlegend": show_legend
    }