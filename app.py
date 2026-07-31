import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rachão Castelo Branco", page_icon="⚽", layout="wide")

st.title("⚽ Rachão Castelo Branco - 2026")

# ID do Arquivo e da Aba
FILE_ID = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"
GID = "1092123094"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=csv&gid={GID}"

# Definimos ttl=0 para forçar o Streamlit a sempre buscar os dados mais recentes sem cache
@st.cache_data(ttl=0)
def load_data():
    # header=3 faz o Pandas ler a linha 4 da planilha como o verdadeiro cabeçalho
    df = pd.read_csv(CSV_URL, header=3)
    
    # Remove linhas completamente vazias, caso existam
    df = df.dropna(how='all')
    return df

try:
    df = load_data()

    # Limpeza dos nomes das colunas (remove espaços extras)
    df.columns = df.columns.str.strip()

    # Botão manual para forçar a atualização dos dados na tela
    if st.button("🔄 Atualizar Dados Agora"):
        st.cache_data.clear()
        st.rerun()

    # Métricas gerais calculadas dinamicamente
    col1, col2, col3 = st.columns(3)
    
    if "Gols" in df.columns:
        total_gols = pd.to_numeric(df["Gols"], errors='coerce').sum()
        col1.metric("Total de Gols", int(total_gols))
        
    if "Assistências" in df.columns:
        total_ast = pd.to_numeric(df["Assistências"], errors='coerce').sum()
        col2.metric("Total de Assistências", int(total_ast))
        
    if "Gols Contra" in df.columns:
        total_gc = pd.to_numeric(df["Gols Contra"], errors='coerce').sum()
        col3.metric("Gols Contra", int(total_gc))

    st.markdown("---")

    # Exibe a tabela formatada e limpa
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Erro ao processar os dados da planilha: {e}")
