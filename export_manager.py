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
import plotly.io as pio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Custom exception for export-related errors"""
    pass


def is_cloud_environment():
    """Check if running in Streamlit Cloud environment"""
    try:
        import os
        # Common indicators of cloud environments
        cloud_indicators = [
            'STREAMLIT_SHARING',
            'STREAMLIT_CLOUD', 
            'RENDER',
            'HEROKU',
            'REPLIT_DEPLOYMENT'
        ]
        return any(indicator in os.environ for indicator in cloud_indicators)
    except:
        return False


class ExportManager:
    """Manages export functionality for plots and data"""
    
    # Default export settings with standard fonts
    DEFAULT_PLOT_CONFIG = {
        "width": 1200,
        "height": 800,
        "margin": dict(l=80, r=120, t=60, b=60),
        "showlegend": False,
        # Standard fonts that work everywhere
        "font_family": "Arial",
        "font_size": 14,
        "font_color": "#000000"
    }
    
    @staticmethod
    def prepare_figure_for_export(fig: go.Figure, 
                                config: Optional[dict] = None) -> go.Figure:
        """
        Prepare figure for export by applying export-specific settings
        CAREFULLY preserving marker symbols
        """
        export_fig = fig.to_dict()  # Deep copy
        export_fig = go.Figure(export_fig)
        
        # Apply basic configuration first
        export_config = {
            "width": 1200,
            "height": 800,
            "margin": dict(l=80, r=120, t=60, b=60),
            "showlegend": False
        }
        if config:
            export_config.update(config)
        
        # Apply ONLY safe layout updates that don't affect markers
        export_fig.update_layout(**export_config)
        
        # Update ONLY specific text elements, avoiding global font changes
        # This preserves marker symbol fonts
        try:
            # Update title font if title exists
            if export_fig.layout.title and export_fig.layout.title.text:
                export_fig.update_layout(
                    title_font_family="Arial",
                    title_font_size=18,
                    title_font_color="#000000"
                )
            
            # Update axes fonts carefully
            export_fig.update_xaxes(
                title_font_family="Arial",
                title_font_size=16, 
                title_font_color="#000000",
                tickfont_family="Arial",
                tickfont_size=12,
                tickfont_color="#000000"
            )
            
            export_fig.update_yaxes(
                title_font_family="Arial",
                title_font_size=16,
                title_font_color="#000000", 
                tickfont_family="Arial",
                tickfont_size=12,
                tickfont_color="#000000"
            )
            
            # Update legend font if legend exists
            if export_fig.layout.showlegend:
                export_fig.update_layout(
                    legend_font_family="Arial",
                    legend_font_size=12,
                    legend_font_color="#000000"
                )
                
        except Exception as e:
            logger.warning(f"Font update warning: {e}")
            # Continue anyway - better to have working export with original fonts
            
        return export_fig
    
    @staticmethod
    def export_plot_html(fig: go.Figure, 
                        filename: Optional[str] = None,
                        config: Optional[dict] = None) -> Tuple[str, str]:
        """
        Export plot as interactive HTML (cloud-friendly fallback)
        
        Args:
            fig: Plotly figure to export
            filename: Custom filename (optional)
            config: Custom export configuration
            
        Returns:
            Tuple of (html_string, filename)
        """
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.html"
            elif not filename.endswith('.html'):
                filename += '.html'
            
            # Export to HTML with embedded plotly.js
            html_string = export_fig.to_html(
                include_plotlyjs='inline',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                }
            )
            
            logger.info(f"Successfully exported HTML: {filename}")
            return html_string, filename
            
        except Exception as e:
            logger.error(f"HTML export failed: {str(e)}")
            raise ExportError(f"Failed to export HTML: {str(e)}")
    
    @staticmethod
    def export_plot_png(fig: go.Figure, 
                       filename: Optional[str] = None,
                       config: Optional[dict] = None) -> Tuple[bytes, str]:
        """
        Export plot as PNG (tries kaleido, falls back to instructions)
        """
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.png"
            elif not filename.endswith('.png'):
                filename += '.png'
            
            # Try kaleido export
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
        Export plot as SVG with web-safe fonts for maximum compatibility
        """
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.svg"
            elif not filename.endswith('.svg'):
                filename += '.svg'
            
            # Try kaleido export
            svg_string = export_fig.to_image(format="svg", engine="kaleido")
            
            # Post-process SVG to ensure font compatibility
            svg_string = svg_string.decode('utf-8') if isinstance(svg_string, bytes) else svg_string
            
            # Replace ONLY text fonts, be careful not to break symbol fonts
            # Look for font-family in text elements, not in marker symbols
            import re
            
            # Replace font families in text elements but preserve symbol fonts
            svg_string = re.sub(
                r'font-family:"[^"]*"(?![^<]*</symbol>)(?![^<]*</marker>)', 
                'font-family:"Arial"', 
                svg_string
            )
            
            # Alternative safer approach - only replace known problematic fonts
            problematic_fonts = [
                'font-family:"Open Sans"',
                'font-family:"Helvetica Neue"', 
                'font-family:"Segoe UI"',
                'font-family:"system-ui"',
                'font-family:"Roboto"'
            ]
            
            for problem_font in problematic_fonts:
                svg_string = svg_string.replace(problem_font, 'font-family:"Arial"')
            
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
        Export plot as PDF with web-safe fonts for maximum compatibility
        """
        try:
            export_fig = ExportManager.prepare_figure_for_export(fig, config)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"geoquick_plot_{timestamp}.pdf"
            elif not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # DON'T override layout fonts - this breaks marker symbols
            # The prepare_figure_for_export already handles text fonts properly
            
            # Try kaleido export with PDF-specific settings
            pdf_bytes = export_fig.to_image(
                format="pdf", 
                engine="kaleido",
                width=export_fig.layout.width,
                height=export_fig.layout.height
            )
            
            logger.info(f"Successfully exported PDF: {filename}")
            return pdf_bytes, filename
            
        except Exception as e:
            logger.error(f"PDF export failed: {str(e)}")
            raise ExportError(f"Failed to export PDF: {str(e)}")


def render_export_buttons(fig: go.Figure, 
                         export_config: Optional[dict] = None,
                         key_prefix: str = "export") -> None:
    """
    Render export buttons in Streamlit interface with cloud-friendly fallbacks
    """
    st.markdown("### 📥 Export Plot")
    
    is_cloud = is_cloud_environment()
    
    if is_cloud:
        # Cloud environment - offer HTML as primary option
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                html_string, filename = ExportManager.export_plot_html(fig, config=export_config)
                st.download_button(
                    label="📊 Save as HTML",
                    data=html_string,
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True,
                    key=f"{key_prefix}_html",
                    help="Interactive HTML file that works in any browser"
                )
            except ExportError as e:
                st.error(f"HTML export failed: {str(e)}")
        
        with col2:
            st.markdown("""
            **📸 For PNG/PDF export:**
            1. Use the camera icon in the plot toolbar above
            2. Or right-click the plot → "Save image as..."
            3. For vector graphics, try the HTML export
            """)
            
    else:
        # Local environment - full functionality
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
            except ExportError:
                st.info("Use camera icon in plot toolbar for PNG export")
        
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
            except ExportError:
                st.info("SVG export not available in cloud")
        
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
            except ExportError:
                st.info("PDF export not available in cloud")


def render_export_settings() -> dict:
    """
    Render export settings UI and return configuration
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