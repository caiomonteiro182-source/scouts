import streamlit as st
import pandas as pd
from PIL import Image
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="FCB - Futebol Castelo Branco",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilização CSS Personalizada (Cores oficiais da Logo: Azul Marinho, Vermelho e Branco)
CUSTOM_CSS = """
<style>
    /* Import de Fontes Esportivas */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    /* Fundo Principal Dark Navy */
    .stApp {
        background-color: #070D18;
        color: #F1F5F9;
    }

    /* Estilo do Cabeçalho Principal */
    .header-container {
        background: linear-gradient(135deg, #0B1B3D 0%, #152844 50%, #C8102E 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(200, 16, 46, 0.25);
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 25px;
        border-left: 6px solid #C8102E;
    }

    .header-title {
        color: #FFFFFF;
        font-size: 32px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .header-subtitle {
        color: #CBD5E1;
        font-size: 14px;
        font-weight: 600;
        margin: 5px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Cards de Métricas e Destaques */
    .metric-card {
        background: #0F2144;
        border: 1px solid #1E3A8A;
        border-top: 4px solid #C8102E;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #C8102E;
    }

    .metric-title {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 36px;
        font-weight: 900;
        margin: 8px 0;
    }

    .metric-sub {
        color: #E2E8F0;
        font-size: 14px;
        font-weight: 600;
    }

    .gold-badge { color: #F59E0B; }
    .silver-badge { color: #38BDF8; }
    .red-badge { color: #EF4444; }

    /* Estilização de Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #0F172A;
        padding: 8px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background-color: #C8102E !important;
        color: #FFFFFF !important;
    }

    /* Botão de Atualização Customizado */
    .stButton>button {
        background: linear-gradient(90deg, #C8102E 0%, #990B20 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(200, 16, 46, 0.3);
        width: 100%;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #E11D48 0%, #C8102E 100%);
        box-shadow: 0 6px 18px rgba(225, 29, 72, 0.5);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Leitura dos Dados do Google Sheets
FILE_ID = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"
GID = "1092123094"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=0)
def load_data():
    df = pd.read_csv(CSV_URL, header=3)
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip()
    
    # Converter colunas numéricas com segurança
    colunas_numericas = ["Gols", "Assistências", "Gols Contra", "Participações em Gols"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Se a coluna de Participações não existir, calcula automaticamente
    if "Participações em Gols" not in df.columns and "Gols" in df.columns and "Assistências" in df.columns:
        df["Participações em Gols"] = df["Gols"] + df["Assistências"]

    return df

# 4. Layout do Cabeçalho Oficial (Com Logo e Título)
col_logo, col_title = st.columns([1, 5])

with col_logo:
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png")
        st.image(logo, width=120)
    else:
        st.markdown("<h1>🛡️</h1>", unsafe_allow_html=True)

with col_title:
    st.markdown("""
        <div class="header-container">
            <div>
                <h1 class="header-title">FUTEBOL CASTELO BRANCO</h1>
                <p class="header-subtitle">PAINEL OFICIAL DE ESTATÍSTICAS • TEMPORADA 2026</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 5. Barra Lateral (Sidebar) com Filtros e Informações
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("### ⚙️ Painel de Controle")
    
    if st.button("🔄 Atualizar Estatísticas"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔍 Filtros da Tabela")

try:
    df = load_data()

    # Filtros na Sidebar
    if "Time" in df.columns:
        times_unicos = ["Todos"] + sorted(list(df["Time"].unique()))
        filtro_time = st.sidebar.selectbox("Colete / Time:", times_unicos)
    else:
        filtro_time = "Todos"

    busca_jogador = st.sidebar.text_input("Buscar Atleta por Nome:", "")

    # Aplicação dos Filtros
    df_filtrado = df.copy()
    if filtro_time != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Time"] == filtro_time]
    if busca_jogador:
        df_filtrado = df_filtrado[df_filtrado["Jogador"].str.contains(busca_jogador, case=False, na=False)]

    # Ordenar por Gols e Assistências
    df_filtrado = df_filtrado.sort_values(by=["Gols", "Assistências", "Participações em Gols"], ascending=False)

    # 6. Destaques da Temporada (Cards de Top Performers)
    artilheiro = df.sort_values(by="Gols", ascending=False).iloc[0] if not df.empty else None
    garcom = df.sort_values(by="Assistências", ascending=False).iloc[0] if not df.empty else None
    lider_participacoes = df.sort_values(by="Participações em Gols", ascending=False).iloc[0] if not df.empty else None

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        total_g = df["Gols"].sum()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⚽ Total de Gols</div>
                <div class="metric-value">{total_g}</div>
                <div class="metric-sub">Marcados em 2026</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        if artilheiro is not None:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🥇 Artilheiro Principal</div>
                    <div class="metric-value gold-badge">{artilheiro['Gols']} <span style="font-size:16px;">gols</span></div>
                    <div class="metric-sub">👑 {artilheiro['Jogador']} ({artilheiro['Time']})</div>
                </div>
            """, unsafe_allow_html=True)

    with c3:
        if garcom is not None:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🎯 Rei das Assistências</div>
                    <div class="metric-value silver-badge">{garcom['Assistências']} <span style="font-size:16px;">ast</span></div>
                    <div class="metric-sub">👟 {garcom['Jogador']} ({garcom['Time']})</div>
                </div>
            """, unsafe_allow_html=True)

    with c4:
        if lider_participacoes is not None:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🔥 Maior Participação</div>
                    <div class="metric-value red-badge">{lider_participacoes['Participações em Gols']} <span style="font-size:16px;">G+A</span></div>
                    <div class="metric-sub">⚡ {lider_participacoes['Jogador']} ({lider_participacoes['Time']})</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 7. Abas de Conteúdo
    aba1, aba2, aba3 = st.tabs(["🏆 Classificação Geral", "⚔️ Duelo de Coletes (Times)", "🏅 Top 3 Artilharia"])

    with aba1:
        st.subheader("📋 Tabela Completa de Desempenho")
        
        # Formatação e Exibição da Tabela com Streamlit Dataframe
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Jogador": st.column_config.TextColumn("Atleta 🏃", help="Nome do Jogador"),
                "Time": st.column_config.TextColumn("Colete 👕", help="Time do Atleta"),
                "Gols": st.column_config.NumberColumn("Gols ⚽", format="%d"),
                "Assistências": st.column_config.NumberColumn("Assistências 🎯", format="%d"),
                "Gols Contra": st.column_config.NumberColumn("Gols Contra ⚠️", format="%d"),
                "Participações em Gols": st.column_config.NumberColumn("Participações (G+A) 🔥", format="%d"),
            }
        )

    with aba2:
        st.subheader("⚔️ Comparativo: Colete Vermelho vs Colete Azul")
        if "Time" in df.columns:
            stats_times = df.groupby("Time")[["Gols", "Assistências", "Gols Contra", "Participações em Gols"]].sum().reset_index()
            
            col_vermelho, col_azul = st.columns(2)
            
            df_v = stats_times[stats_times["Time"] == "Vermelho"]
            df_a = stats_times[stats_times["Time"] == "Azul"]

            with col_vermelho:
                gols_v = df_v["Gols"].values[0] if not df_v.empty else 0
                ast_v = df_v["Assistências"].values[0] if not df_v.empty else 0
                st.markdown(f"""
                    <div style="background-color: #3f0a14; border: 2px solid #C8102E; padding: 20px; border-radius: 12px; text-align: center;">
                        <h2 style="color: #EF4444; margin: 0;">🔴 COLETE VERMELHO</h2>
                        <h1 style="color: #FFF; font-size: 48px; margin: 10px 0;">{gols_v} <span style="font-size: 20px;">GOLS</span></h1>
                        <p style="color: #CBD5E1; font-weight: 600;">{ast_v} Assistências Totais</p>
                    </div>
                """, unsafe_allow_html=True)

            with col_azul:
                gols_a = df_a["Gols"].values[0] if not df_a.empty else 0
                ast_a = df_a["Assistências"].values[0] if not df_a.empty else 0
                st.markdown(f"""
                    <div style="background-color: #0A1E3F; border: 2px solid #38BDF8; padding: 20px; border-radius: 12px; text-align: center;">
                        <h2 style="color: #38BDF8; margin: 0;">🔵 COLETE AZUL</h2>
                        <h1 style="color: #FFF; font-size: 48px; margin: 10px 0;">{gols_a} <span style="font-size: 20px;">GOLS</span></h1>
                        <p style="color: #CBD5E1; font-weight: 600;">{ast_a} Assistências Totais</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(stats_times, use_container_width=True, hide_index=True)

    with aba3:
        st.subheader("🏅 Pódio da Artilharia")
        top3_gols = df.sort_values(by="Gols", ascending=False).head(3)
        
        cols_podio = st.columns(3)
        podio_icons = ["🥇 1º Lugar", "🥈 2º Lugar", "🥉 3º Lugar"]
        podio_colors = ["#F59E0B", "#94A3B8", "#D97706"]
        
        for idx, (_, row) in enumerate(top3_gols.iterrows()):
            with cols_podio[idx]:
                st.markdown(f"""
                    <div style="background: #0F2144; border-top: 5px solid {podio_colors[idx]}; padding: 20px; border-radius: 12px; text-align: center;">
                        <h3 style="color: {podio_colors[idx]}; margin: 0;">{podio_icons[idx]}</h3>
                        <h2 style="color: #FFF; margin: 10px 0;">{row['Jogador']}</h2>
                        <h1 style="color: {podio_colors[idx]}; margin: 0;">{row['Gols']} <span style="font-size: 16px;">Gols</span></h1>
                        <p style="color: #94A3B8; margin-top: 5px;">Time: {row['Time']} | {row['Assistências']} Assistências</p>
                    </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar dados da planilha: {e}")
