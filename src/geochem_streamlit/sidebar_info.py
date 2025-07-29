import streamlit as st


def show_sidebar_info() -> None:
    st.sidebar.markdown("""
    ## 🌋👋 GeoQuick  
    **1. Upload a file or link to a table (Google Sheets)**  
    - *Choose scatter plot or box plot (scatter is default)*  
    - *For scatter plot, select a column for the X-axis and Y-axis and a column for grouping (optional)*  
    - *For box plot, select a column for the Y-axis and grouping variable (X-axis does not need to be specified), use any column*  
    - *For scatter plot, select x and y axes*  
    - *For both plots, select a column for grouping (optional)*  
                        
    **2. Add filters (click Enter after input value), customize style**  
    **3. Export style (JSON) or image (.png, .pdf)**

    ℹ️ For Google Sheets: insert a public link (see example below, copy example link to your clipboard and paste it into the input field, then press Enter).
    """)

    with st.sidebar.expander("Example Google Sheets link"):
        st.markdown(
            "https://docs.google.com/spreadsheets/d/1w34ppQgaNuAhQXO16RI8QwtJROPldspvEUAnMaeLuyU/export?format=csv"
        )

    st.sidebar.markdown(
        "**💡 Ideas, feedback?**\n"
        "[Your form is here](https://forms.gle/Hv7LfRTGpUu8kXMR9) 📝",
        unsafe_allow_html=True,
    )
