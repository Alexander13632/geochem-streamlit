import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def load_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)


def get_dataframe_from_gsheet(gs_url: str):
    try:
        # Принимаем сразу рабочие CSV-ссылки
        if "export?format=csv" in gs_url or "output=csv" in gs_url:
            csv_url = gs_url
        elif "/edit" in gs_url:
            csv_url = gs_url.split("/edit")[0] + "/export?format=csv"
        elif "/view" in gs_url:
            csv_url = gs_url.split("/view")[0] + "/export?format=csv"
        else:
            st.error("Incorrect link to Google Sheets!")
            return pd.DataFrame(), False
        df = pd.read_csv(csv_url)
        st.success("Data from Google Sheets loaded successfully!")
        return df, True
    except Exception as e:
        st.error(f"Error reading Google Sheets: {e}")
        return pd.DataFrame(), False



def get_dataframe():
    gs_url = st.sidebar.text_input("Insert link to Google Sheets (optional):", value="")
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV/TXT/XLSX-file", type=["csv", "txt", "xls", "xlsx"]
    )
    user_data = False

    if gs_url.strip():
        df, user_data = get_dataframe_from_gsheet(gs_url)
        if not df.empty:
            return df, user_data
        # если не удалось — идём дальше

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                df = pd.read_csv(uploaded_file, sep='\t')
            else:
                df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            return df, True
        except Exception as e:
            st.error(f"Error reading file: {e}")
            # fallback

    # Дефолтные данные
    try:
        df = load_csv(st.secrets["CSV_URL"])
        return df, False
    except Exception as e:
        st.error(f"Error loading default data: {e}")
        return pd.DataFrame(), False
