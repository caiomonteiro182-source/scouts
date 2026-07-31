import streamlit as st
import pandas as pd
import os
import base64
import requests
import textwrap
from datetime import datetime, timedelta

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

    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none !important;
    }

    .stApp {
        background-color: #070D18;
        color: #F1F5F9;
    }

    /* Centralizar conteúdo das células e cabeçalhos do st.dataframe */
    [data-testid="stDataFrame"] div[role="gridcell"] {
        justify-content: center !important;
        text-align: center !important;
    }
    [data-testid="stDataFrame"] div[role="columnheader"] {
        justify-content: center !important;
        text-align: center !important;
    }

    /* Banner do Cabeçalho Oficial */
    .header-container {
        background: linear-gradient(135deg, #0B1B3D 0%, #152844 60%, #C8102E 100%);
        padding: 25px 40px;
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(200, 16, 46, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 35px;
        margin-bottom: 20px;
        border-left: 6px solid #C8102E;
        text-align: left;
    }

    .header-title {
        color: #FFFFFF;
        font-size: 38px;
        font-weight: 900;
        margin: 0;
        letter-spacing: 2px;
        text-transform: uppercase;
        line-height: 1.1;
    }

    .header-subtitle {
        color: #CBD5E1;
        font-size: 14px;
        font-weight: 600;
        margin: 8px 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Cards Informativos Topo */
    .info-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .card-border-blue { border-left: 5px solid #38BDF8; }
    .card-border-gold { border-left: 5px solid #F59E0B; }

    .card-tag {
        color: #38BDF8;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .card-tag-gold {
        color: #F59E0B;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .card-main-text {
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 700;
        margin-top: 4px;
    }

    .weather-pill {
        background-color: #0F2144;
        border: 1px solid #1E3A8A;
        border-radius: 20px;
        padding: 4px 12px;
        color: #F1F5F9;
        font-size: 13px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 8px;
    }

    /* Placar Visual de Vitórias */
    .scoreboard-box {
        display: flex;
        align-items: center;
        justify-content: space-around;
        background-color: #0B1329;
        border-radius: 10px;
        padding: 10px 15px;
        margin-top: 8px;
        border: 1px solid #1E293B;
    }

    .team-score {
        font-size: 18px;
        font-weight: 900;
    }
    .score-red { color: #EF4444; }
    .score-blue { color: #38BDF8; }
    .score-divider { color: #64748B; font-weight: 900; font-size: 16px; }

    /* Cards de Métricas */
    .metric-card {
        background: #0F2144;
        border: 1px solid #1E3A8A;
        border-top: 4px solid #C8102E;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
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

    /* Navegação por Pílulas */
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

    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(90deg, #C8102E 0%, #990B20 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(200, 16, 46, 0.4) !important;
    }

    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }

    /* Cards do Elenco */
    .roster-card {
        background-color: #0F172A;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .roster-header-vermelho {
        border-bottom: 3px solid #C8102E;
        padding-bottom: 10px;
        margin-bottom: 15px;
        color: #EF4444;
        font-weight: 900;
    }
    .roster-header-azul {
        border-bottom: 3px solid #38BDF8;
        padding-bottom: 10px;
        margin-bottom: 15px;
        color: #38BDF8;
        font-weight: 900;
    }
    .pos-section-title {
        color: #F1F5F9;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 8px;
    }
    .player-pill {
        background: #1E293B;
        color: #CBD5E1;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin: 3px 2px;
        border: 1px solid #334155;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 3. CARREGAMENTO DAS DUAS PLANILHAS E CLIMA
# ==========================================
# 1. Planilha de Gols e Assistências
ID_PLANILHA_STATS = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"
URL_STATS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_STATS}/export?format=csv"

# 2. Planilha de Vitórias dos Times
ID_PLANILHA_VITORIAS = "1e9VpoNzzqYZlD8JFJxWLQiWhNw4AaKiycauCZDxAas0"
GID_VITORIAS = "1092123094"
URL_VITORIAS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_VITORIAS}/export?format=csv&gid={GID_VITORIAS}"

@st.cache_data(ttl=0)
def load_player_stats():
    """Carrega as estatísticas dos jogadores (Gols, Assistências)."""
    df = pd.read_csv(URL_STATS, header=3)
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip()
    
    colunas_numericas = ["Gols", "Assistências", "Gols Contra", "Participações em Gols"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    if "Participações em Gols" not in df.columns and "Gols" in df.columns and "Assistências" in df.columns:
        df["Participações em Gols"] = df["Gols"] + df["Assistências"]

    return df

@st.cache_data(ttl=0)
def load_victories_stats():
    """Carrega o placar de vitórias por time da planilha dedicada."""
    try:
        df_vic = pd.read_csv(URL_VITORIAS)
        df_vic.columns = df_vic.columns.str.strip()
        return df_vic
    except Exception:
        return pd.read_csv(f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_VITORIAS}/export?format=csv")

@st.cache_data(ttl=3600)
def get_next_saturday_weather():
    """Calcula dinamicamente o próximo sábado e busca o clima correspondente."""
    try:
        today = datetime.now()
        days_until_saturday = (5 - today.weekday()) % 7
        
        if days_until_saturday == 0 and today.hour >= 18:
            days_until_saturday = 7
        
        next_saturday = today + timedelta(days=days_until_saturday)
        date_str = next_saturday.strftime("%d/%m")

        lat, lon = -23.2758, -51.2783
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_probability,weather_code&timezone=America%2FSao_Paulo"
        
        res = requests.get(url, timeout=5).json()
        hourly = res.get("hourly", {})
        times = hourly.get("time", [])

        target_time_str = next_saturday.strftime("%Y-%m-%dT16:00")
        
        if target_time_str in times:
            idx = times.index(target_time_str)
            temp = hourly["temperature_2m"][idx]
            pop = hourly["precipitation_probability"][idx]
            wcode = hourly["weather_code"][idx]

            if wcode == 0:
                icon = "☀️ Céu Limpo"
            elif wcode in [1, 2, 3]:
                icon = "⛅ Parcialmente Nublado" if wcode in [1, 2] else "☁️ Nublado"
            elif wcode in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
                icon = "🌧️ Chuva"
            elif wcode in [95, 96, 99]:
                icon = "⛈️ Tempestade"
            else:
                icon = "🌤️ Tempo Bom"

            return {
                "data": date_str,
                "temp": f"{int(round(temp))}°C",
                "pop": f"{pop}%",
                "condicao": icon,
                "status": True
            }
        else:
            return {"data": date_str, "status": False}
    except Exception:
        return {"data": "", "status": False}

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ==========================================
# 4. CABEÇALHO OFICIAL
# ==========================================
try:
    logo_base64 = get_base64_of_bin_file("logo.png")
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 140px; width: auto; object-fit: contain;">'
except:
    logo_html = '<h1 style="margin:0; font-size: 70px;">🛡️</h1>'

header_code = f"""
<div class="header-container">
    <div>{logo_html}</div>
    <div>
        <h1 class="header-title">FUTEBOL CASTELO BRANCO</h1>
        <p class="header-subtitle">PAINEL OFICIAL DE ESTATÍSTICAS • TEMPORADA 2026</p>
    </div>
</div>
"""
st.markdown(textwrap.dedent(header_code), unsafe_allow_html=True)

# ==========================================
# 5. CARDS SUPERIORES (PRÓXIMO JOGO & PLACAR DE VITÓRIAS)
# ==========================================
df_players = load_player_stats()
df_vitorias = load_victories_stats()

# Extração automática das vitórias de cada time da segunda planilha
vitorias_vermelho = 0
vitorias_azul = 0

try:
    for idx, row in df_vitorias.iterrows():
        row_str = str(row.values).lower()
        nums = [int(val) for val in row if str(val).isdigit()]
        if "vermelho" in row_str and nums:
            vitorias_vermelho = nums[0]
        elif "azul" in row_str and nums:
            vitorias_azul = nums[0]
except Exception:
    pass

weather_info = get_next_saturday_weather()

if weather_info["status"]:
    weather_html = (
        f'<div class="weather-pill">'
        f'<span>{weather_info["condicao"]}</span> • '
        f'<span>🌡️ {weather_info["temp"]}</span> • '
        f'<span>🌧️ Chance de Chuva: <b>{weather_info["pop"]}</b></span>'
        f'</div>'
    )
else:
    weather_html = '<div class="weather-pill">⚽ Dia de Jogo Confirmado</div>'

data_jogo = weather_info.get('data', '')
data_str = f" ({data_jogo})" if data_jogo else ""

col_jogo, col_placar = st.columns(2)

with col_jogo:
    card_jogo_html = (
        f'<div class="info-card card-border-blue">'
        f'<div class="card-tag">📍 PRÓXIMO ENCONTRO</div>'
        f'<div class="card-main-text">Sábado{data_str} às 16:00 • Cambé - PR</div>'
        f'<div>{weather_html}</div>'
        f'</div>'
    )
    st.markdown(card_jogo_html, unsafe_allow_html=True)

with col_placar:
    card_placar_html = (
        f'<div class="info-card card-border-gold">'
        f'<div class="card-tag-gold">🏆 PLACAR GERAL DE VITÓRIAS</div>'
        f'<div class="scoreboard-box">'
        f'<span class="team-score score-red">🔴 Vermelho: {vitorias_vermelho}</span>'
        f'<span class="score-divider">X</span>'
        f'<span class="team-score score-blue">🔵 Azul: {vitorias_azul}</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_placar_html, unsafe_allow_html=True)

# ==========================================
# 6. CARDS DE DESTAQUES RÁPIDOS
# ==========================================
try:
    artilheiro = df_players.sort_values(by="Gols", ascending=False).iloc[0] if not df_players.empty else None
    garcom = df_players.sort_values(by="Assistências", ascending=False).iloc[0] if not df_players.empty else None
    lider_participacoes = df_players.sort_values(by="Participações em Gols", ascending=False).iloc[0] if not df_players.empty else None

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        total_g = df_players["Gols"].sum()
        card_total = (
            f'<div class="metric-card">'
            f'<div class="metric-title">⚽ TOTAL DE GOLS</div>'
            f'<div class="metric-value">{total_g}</div>'
            f'<div class="metric-sub">Marcados em 2026</div>'
            f'</div>'
        )
        st.markdown(card_total, unsafe_allow_html=True)

    with c2:
        if artilheiro is not None:
            card_artilheiro = (
                f'<div class="metric-card">'
                f'<div class="metric-title">🥇 ARTILHEIRO PRINCIPAL</div>'
                f'<div class="metric-value gold-badge">{artilheiro["Gols"]} <span style="font-size:16px;">gols</span></div>'
                f'<div class="metric-sub">👑 {artilheiro["Jogador"]} ({artilheiro["Time"]})</div>'
                f'</div>'
            )
            st.markdown(card_artilheiro, unsafe_allow_html=True)

    with c3:
        if garcom is not None:
            card_garcom = (
                f'<div class="metric-card">'
                f'<div class="metric-title">🎯 REI DAS ASSISTÊNCIAS</div>'
                f'<div class="metric-value silver-badge">{garcom["Assistências"]} <span style="font-size:16px;">ast</span></div>'
                f'<div class="metric-sub">👟 {garcom["Jogador"]} ({garcom["Time"]})</div>'
                f'</div>'
            )
            st.markdown(card_garcom, unsafe_allow_html=True)

    with c4:
        if lider_participacoes is not None:
            card_part = (
                f'<div class="metric-card">'
                f'<div class="metric-title">🔥 MAIOR PARTICIPAÇÃO</div>'
                f'<div class="metric-value red-badge">{lider_participacoes["Participações em Gols"]} <span style="font-size:16px;">G+A</span></div>'
                f'<div class="metric-sub">⚡ {lider_participacoes["Jogador"]} ({lider_participacoes["Time"]})</div>'
                f'</div>'
            )
            st.markdown(card_part, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 7. NAVEGAÇÃO POR PÍLULAS
    # ==========================================
    opcao_aba = st.radio(
        label="",
        options=["🏆 Classificação Geral", "👥 Elenco dos Times", "⚔️ Duelo de Times", "🏅 Top 3 Artilharia"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # CONTEÚDO DE CADA ABA
    if opcao_aba == "🏆 Classificação Geral":
        st.subheader("📋 Tabela Completa de Desempenho")
        
        col_filtro1, col_filtro2 = st.columns([1, 2])
        
        with col_filtro1:
            if "Time" in df_players.columns:
                times_unicos = ["Todos os Times"] + sorted(list(df_players["Time"].dropna().unique()))
                filtro_time = st.selectbox("Filtrar por Time:", times_unicos)
            else:
                filtro_time = "Todos os Times"

        with col_filtro2:
            busca_jogador = st.text_input("Buscar Atleta por Nome:", "", placeholder="Digite o nome do jogador...")

        df_filtrado = df_players.copy()
        if filtro_time != "Todos os Times":
            df_filtrado = df_filtrado[df_filtrado["Time"] == filtro_time]
        if busca_jogador:
            df_filtrado = df_filtrado[df_filtrado["Jogador"].str.contains(busca_jogador, case=False, na=False)]

        df_filtrado = df_filtrado.sort_values(by=["Gols", "Assistências", "Participações em Gols"], ascending=False)

        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Jogador": st.column_config.TextColumn("Atleta 🏃", alignment="center"),
                "Time": st.column_config.TextColumn("Time 👕", alignment="center"),
                "Gols": st.column_config.NumberColumn("Gols ⚽", format="%d", alignment="center"),
                "Assistências": st.column_config.NumberColumn("Assistências 🎯", format="%d", alignment="center"),
                "Gols Contra": st.column_config.NumberColumn("Gols Contra ⚠️", format="%d", alignment="center"),
                "Participações em Gols": st.column_config.NumberColumn("Participações (G+A) 🔥", format="%d", alignment="center"),
            }
        )

    elif opcao_aba == "👥 Elenco dos Times":
        st.subheader("👥 Elenco Oficial dos Times")

        elenco_vermelho = {
            "Goleiros": ["Vozinha"],
            "Zagueiros": ["Nilton", "Carlão (TCR)", "Camarão Sergipano"],
            "Laterais": ["Paulo Base", "Samuel", "Cezar", "Gledson"],
            "Meias": ["Cassiano", "Alessandro", "Mateus Rocha", "Diego (Lucas Lima)", "Cristiano", "Manoel"],
            "Atacantes": ["Nata", "Izaqui"]
        }

        elenco_azul = {
            "Goleiros": ["Jonathan", "Matheus"],
            "Zagueiros": ["Gabigol", "Wellington", "Joel"],
            "Laterais": ["Caio", "Otero", "Cristoffer", "Jefferson"],
            "Meias": ["Ian", "Juel", "Gabriel"],
            "Atacantes": ["Tavinho", "P.H", "Maradona"]
        }

        col_v, col_a = st.columns(2)

        icones_pos = {
            "Goleiros": "🧤",
            "Zagueiros": "🛡️",
            "Laterais": "🏃‍♂️",
            "Meias": "🧠",
            "Atacantes": "⚡"
        }

        with col_v:
            st.markdown('<div class="roster-card"><div class="roster-header-vermelho"><h2>🔴 TIME VERMELHO</h2></div>', unsafe_allow_html=True)
            for pos, jogadores in elenco_vermelho.items():
                st.markdown(f'<div class="pos-section-title">{icones_pos.get(pos, "⚽")} {pos}</div>', unsafe_allow_html=True)
                pills_html = "".join([f'<span class="player-pill">{j}</span>' for j in jogadores])
                st.markdown(f'<div>{pills_html}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_a:
            st.markdown('<div class="roster-card"><div class="roster-header-azul"><h2>🔵 TIME AZUL</h2></div>', unsafe_allow_html=True)
            for pos, jogadores in elenco_azul.items():
                st.markdown(f'<div class="pos-section-title">{icones_pos.get(pos, "⚽")} {pos}</div>', unsafe_allow_html=True)
                pills_html = "".join([f'<span class="player-pill">{j}</span>' for j in jogadores])
                st.markdown(f'<div>{pills_html}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif opcao_aba == "⚔️ Duelo de Times":
        st.subheader("⚔️ Comparativo: Time Vermelho vs Time Azul")
        if "Time" in df_players.columns:
            stats_times = df_players.groupby("Time")[["Gols", "Assistências", "Gols Contra", "Participações em Gols"]].sum().reset_index()
            
            col_vermelho, col_azul = st.columns(2)
            
            df_v = stats_times[stats_times["Time"] == "Vermelho"]
            df_a = stats_times[stats_times["Time"] == "Azul"]

            with col_vermelho:
                gols_v = df_v["Gols"].values[0] if not df_v.empty else 0
                ast_v = df_v["Assistências"].values[0] if not df_v.empty else 0
                card_v = (
                    f'<div style="background-color: #3f0a14; border: 2px solid #C8102E; padding: 20px; border-radius: 12px; text-align: center;">'
                    f'<h2 style="color: #EF4444; margin: 0;">🔴 TIME VERMELHO</h2>'
                    f'<h1 style="color: #FFF; font-size: 48px; margin: 10px 0;">{gols_v} <span style="font-size: 20px;">GOLS</span></h1>'
                    f'<p style="color: #CBD5E1; font-weight: 600;">{ast_v} Assistências Totais</p>'
                    f'</div>'
                )
                st.markdown(card_v, unsafe_allow_html=True)

            with col_azul:
                gols_a = df_a["Gols"].values[0] if not df_a.empty else 0
                ast_a = df_a["Assistências"].values[0] if not df_a.empty else 0
                card_a = (
                    f'<div style="background-color: #0A1E3F; border: 2px solid #38BDF8; padding: 20px; border-radius: 12px; text-align: center;">'
                    f'<h2 style="color: #38BDF8; margin: 0;">🔵 TIME AZUL</h2>'
                    f'<h1 style="color: #FFF; font-size: 48px; margin: 10px 0;">{gols_a} <span style="font-size: 20px;">GOLS</span></h1>'
                    f'<p style="color: #CBD5E1; font-weight: 600;">{ast_a} Assistências Totais</p>'
                    f'</div>'
                )
                st.markdown(card_a, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(stats_times, use_container_width=True, hide_index=True)

    elif opcao_aba == "🏅 Top 3 Artilharia":
        st.subheader("🏅 Pódio da Artilharia")
        top3_gols = df_players.sort_values(by="Gols", ascending=False).head(3)
        
        cols_podio = st.columns(3)
        podio_icons = ["🥇 1º Lugar", "🥈 2º Lugar", "🥉 3º Lugar"]
        podio_colors = ["#F59E0B", "#94A3B8", "#D97706"]
        
        for idx, (_, row) in enumerate(top3_gols.iterrows()):
            with cols_podio[idx]:
                card_podio = (
                    f'<div style="background: #0F2144; border-top: 5px solid {podio_colors[idx]}; padding: 20px; border-radius: 12px; text-align: center;">'
                    f'<h3 style="color: {podio_colors[idx]}; margin: 0;">{podio_icons[idx]}</h3>'
                    f'<h2 style="color: #FFF; margin: 10px 0;">{row["Jogador"]}</h2>'
                    f'<h1 style="color: {podio_colors[idx]}; margin: 0;">{row["Gols"]} <span style="font-size: 16px;">Gols</span></h1>'
                    f'<p style="color: #94A3B8; margin-top: 5px;">Time: {row["Time"]} | {row["Assistências"]} Assistências</p>'
                    f'</div>'
                )
                st.markdown(card_podio, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar dados das planilhas: {e}")
