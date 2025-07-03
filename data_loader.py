import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def load_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

def get_dataframe():
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV/TXT/XLSX-file", type=["csv", "txt", "xls", "xlsx"]
    )
    user_data = False

    if uploaded_file is not None:
        user_data = True
        try:
            if uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                df = pd.read_csv(uploaded_file, sep='\t')
            else:
                df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            df = load_csv(st.secrets["CSV_URL"])
            user_data = False
    else:
        df = load_csv(st.secrets["CSV_URL"])
    return df, user_data
