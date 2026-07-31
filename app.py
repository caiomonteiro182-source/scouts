import streamlit as st
import pandas as pd
import os
import base64

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="FCB - Futebol Castelo Branco",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. ESTILIZAÇÃO CSS PERSONALIZADA (FCB THEME)
# ==========================================
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    /* Oculta a barra lateral do Streamlit */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Fundo Escuro Esportivo */
    .stApp {
        background-color: #070D18;
        color: #F1F5F9;
    }

    /* Banner do Cabeçalho Oficial */
    .header-container {
        background: linear-gradient(135deg, #0B1B3D 0%, #152844 60%, #C8102E 100%);
        padding: 20px 30px;
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(200, 16, 46, 0.25);
        display: flex;
        align-items: center;
        gap: 25px;
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
        line-height: 1.1;
    }

    .header-subtitle {
        color: #CBD5E1;
        font-size: 13px;
        font-weight: 600;
        margin: 6px 0 0 0;
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
        font-size: 11px;
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
        font-size: 13px;
        font-weight: 600;
    }

    .gold-badge { color: #F59E0B; }
    .silver-badge { color: #38BDF8; }
    .red-badge { color: #EF4444; }

    /* ==========================================
       ESTILO DAS PÍLULAS / CÍRCULOS DE NAVEGAÇÃO
       ========================================== */
    div[data-testid="stRadio"] > div {
        background-color: #0F172A;
        padding: 8px 12px;
        border-radius: 50px;
        display: inline-flex;
        gap: 10px;
        border: 1px solid #1E293B;
    }

    div[data-testid="stRadio"] label {
        background-color: transparent !important;
        color: #94A3B8 !important;
        border-radius: 30px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        border: none !important;
        margin: 0 !important;
    }

    div[data-testid="stRadio"] label:hover {
        color: #FFFFFF !important;
        background-color: rgba(200, 16, 46, 0.2) !important;
    }

    /* Pílula Selecionada (Arredondada/Círculo) */
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(90deg, #C8102E 0%, #990B20 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(200, 16, 46, 0.4) !important;
    }

    /* Esconde a bolinha de rádio padrão */
    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }

    /* Botão Vermelho Oficial FCB */
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

# ==========================================
# 3. CARREGAMENTO DOS DADOS (GOOGLE SHEETS)
# ==========================================
FILE_ID = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"
GID = "1092123094"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{FILE_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=0)
def load_data():
    df = pd.read_csv(CSV_URL, header=3)
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip()
    
    colunas_numericas = ["Gols", "Assistências", "Gols Contra", "Participações em Gols"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    if "Participações em Gols" not in df.columns and "Gols" in df.columns and "Assistências" in df.columns:
        df["Participações em Gols"] = df["Gols"] + df["Assistências"]

    return df

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ==========================================
# 4. CABEÇALHO OFICIAL + BOTÃO ATUALIZAR
# ==========================================
try:
    logo_base64 = get_base64_of_bin_file("logo.png")
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 100px; width: auto; object-fit: contain;">'
except:
    logo_html = '<h1 style="margin:0; font-size: 50px;">🛡️</h1>'

col_header, col_btn = st.columns([5, 1], vertical_alignment="center")

with col_header:
    st.markdown(f"""
        <div class="header-container" style="margin-bottom: 0;">
            <div>
                {logo_html}
            </div>
            <div>
                <h1 class="header-title">FUTEBOL CASTELO BRANCO</h1>
                <p class="header-subtitle">PAINEL OFICIAL DE ESTATÍSTICAS • TEMPORADA 2026</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_btn:
    if st.button("🔄 Atualizar Estatísticas"):
        st.cache_data.clear()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. CONTEÚDO PRINCIPAL
# ==========================================
try:
    df = load_data()

    # Cards de Destaques Rápidos
    artilheiro = df.sort_values(by="Gols", ascending=False).iloc[0] if not df.empty else None
    garcom = df.sort_values(by="Assistências", ascending=False).iloc[0] if not df.empty else None
    lider_participacoes = df.sort_values(by="Participações em Gols", ascending=False).iloc[0] if not df.empty else None

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        total_g = df["Gols"].sum()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⚽ TOTAL DE GOLS</div>
                <div class="metric-value">{total_g}</div>
                <div class="metric-sub">Marcados em 2026</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        if artilheiro is not None:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🥇 ARTILHEIRO PRINCIPAL</div>
                    <div class="metric-value gold-badge">{artilheiro['Gols']} <span style="font-size:16px;">gols</span></div>
                    <div class="metric-sub">👑 {artilheiro['Jogador']} ({artilheiro['Time']})</div>
                </div>
            """, unsafe_allow_html=True)

    with c3:
        if garcom is not None:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🎯 REI DAS ASSISTÊNCIAS</div>
                    <div class="metric-value silver-badge">{garcom['Assistências']} <span style="font-size:16px;">ast</span></div>
                    <div class="metric-sub">👟 {garcom['Jogador']} ({garcom['Time']})</div>
                </div>
            """, unsafe_allow_html=True)

    with c4:
        if lider_participacoes is not None:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🔥 MAIOR PARTICIPAÇÃO</div>
                    <div class="metric-value red-badge">{lider_participacoes['Participações em Gols']} <span style="font-size:16px;">G+A</span></div>
                    <div class="metric-sub">⚡ {lider_participacoes['Jogador']} ({lider_participacoes['Time']})</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 6. NAVEGAÇÃO POR PÍLULAS/CÍRCULOS
    # ==========================================
    opcao_aba = st.radio(
        label="",
        options=["🏆 Classificação Geral", "⚔️ Duelo de Coletes", "🏅 Top 3 Artilharia"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # CONTEÚDO DE CADA ABA
    if opcao_aba == "🏆 Classificação Geral":
        st.subheader("📋 Tabela Completa de Desempenho")
        
        col_filtro1, col_filtro2 = st.columns([1, 2])
        
        with col_filtro1:
            if "Time" in df.columns:
                times_unicos = ["Todos os Coletes"] + sorted(list(df["Time"].dropna().unique()))
                filtro_time = st.selectbox("Filtrar por Colete:", times_unicos)
            else:
                filtro_time = "Todos os Coletes"

        with col_filtro2:
            busca_jogador = st.text_input("Buscar Atleta por Nome:", "", placeholder="Digite o nome do jogador...")

        df_filtrado = df.copy()
        if filtro_time != "Todos os Coletes":
            df_filtrado = df_filtrado[df_filtrado["Time"] == filtro_time]
        if busca_jogador:
            df_filtrado = df_filtrado[df_filtrado["Jogador"].str.contains(busca_jogador, case=False, na=False)]

        df_filtrado = df_filtrado.sort_values(by=["Gols", "Assistências", "Participações em Gols"], ascending=False)

        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Jogador": st.column_config.TextColumn("Atleta 🏃"),
                "Time": st.column_config.TextColumn("Colete 👕"),
                "Gols": st.column_config.NumberColumn("Gols ⚽", format="%d"),
                "Assistências": st.column_config.NumberColumn("Assistências 🎯", format="%d"),
                "Gols Contra": st.column_config.NumberColumn("Gols Contra ⚠️", format="%d"),
                "Participações em Gols": st.column_config.NumberColumn("Participações (G+A) 🔥", format="%d"),
            }
        )

    elif opcao_aba == "⚔️ Duelo de Coletes":
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

    elif opcao_aba == "🏅 Top 3 Artilharia":
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
