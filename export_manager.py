"""
Export Manager for GeoQuick - Simple and Cloud-Friendly Version
"""
import logging
from typing import Optional, Tuple
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Custom exception for export-related errors"""
    pass


class ExportManager:
    """Simple export functionality that works everywhere"""
    
    @staticmethod
    def prepare_figure_for_export(fig: go.Figure, 
                                config: Optional[dict] = None) -> go.Figure:
        """Simple figure preparation for export"""
        export_fig = fig.to_dict()  # Deep copy
        export_fig = go.Figure(export_fig)
        
        # Basic export settings
        if config:
            export_fig.update_layout(**config)
        else:
            export_fig.update_layout(
                width=1200,
                height=800,
                margin=dict(l=80, r=120, t=60, b=60),
                showlegend=False
            )
        
        return export_fig
    
    @staticmethod
    def export_plot_png(fig: go.Figure, 
                       filename: Optional[str] = None,
                       config: Optional[dict] = None) -> Tuple[bytes, str]:
        """Export plot as PNG"""
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.png"
            elif not filename.endswith('.png'):
                filename += '.png'
            
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
        """Export plot as SVG"""
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.svg"
            elif not filename.endswith('.svg'):
                filename += '.svg'
            
            svg_string = export_fig.to_image(format="svg", engine="kaleido")
            svg_string = svg_string.decode('utf-8') if isinstance(svg_string, bytes) else svg_string
            
            logger.info(f"Successfully exported SVG: {filename}")
            return svg_string, filename
            
        except Exception as e:
            logger.error(f"SVG export failed: {str(e)}")
            raise ExportError(f"Failed to export SVG: {str(e)}")
    
    @staticmethod
    def export_plot_pdf(fig: go.Figure, 
                       filename: Optional[str] = None,
                       config: Optional[dict] = None) -> Tuple[bytes, str]:
        """Export plot as PDF"""
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.pdf"
            elif not filename.endswith('.pdf'):
                filename += '.pdf'
            
            pdf_bytes = export_fig.to_image(format="pdf", engine="kaleido")
            logger.info(f"Successfully exported PDF: {filename}")
            return pdf_bytes, filename
            
        except Exception as e:
            logger.error(f"PDF export failed: {str(e)}")
            raise ExportError(f"Failed to export PDF: {str(e)}")


def render_export_buttons(fig: go.Figure, 
                         export_config: Optional[dict] = None,
                         key_prefix: str = "export") -> None:
    """Simple export buttons that work everywhere"""
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
        except:
            st.info("📸 Use camera icon in plot toolbar")
    
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
        except:
            st.info("📸 Use camera icon in plot toolbar")
    
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
        except:
            st.info("📸 Use camera icon in plot toolbar")


def render_export_settings() -> dict:
    """Simple export settings"""
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
        
        # Margins
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