import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rachão Castelo Branco", page_icon="⚽", layout="wide")

st.title("⚽ Rachão Castelo Branco - 2026")

# ID do seu arquivo .xlsx no Google Drive
FILE_ID = "SEU_ID_DO_ARQUIVO_XLSX_AQUI"

# Link para download direto do arquivo .xlsx do Drive
EXCEL_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(EXCEL_URL)

try:
    df = load_data()
    st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error("Erro ao ler o arquivo Excel. Verifique o ID e o compartilhamento do arquivo.")