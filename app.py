import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rachão Castelo Branco", page_icon="⚽", layout="wide")
st.title("⚽ Rachão Castelo Branco - 2026")

# Cole o ID da PLANILHA DO GOOGLE criada no passo 5
FILE_ID = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"

# Link para exportação direta em CSV
CSV_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_URL)

try:
    df = load_data()
    
    # Exibe cartões com totais
    c1, c2, c3 = st.columns(3)
    if "Gols" in df.columns:
        c1.metric("Total de Gols", int(df["Gols"].sum()))
    if "Assistências" in df.columns:
        c2.metric("Total de Assistências", int(df["Assistências"].sum()))
    if "Gols Contra" in df.columns:
        c3.metric("Gols Contra", int(df["Gols Contra"].sum()))

    st.markdown("---")
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro ao ler os dados: {e}")
