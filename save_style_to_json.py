import json
import streamlit as st


def export_style(style_dict):
    style_json = json.dumps(style_dict, indent=2, ensure_ascii=False)
    st.download_button(
        label="Save Style to JSON",
        data=style_json,
        file_name="my_style.json",
        mime="application/json",
    )
