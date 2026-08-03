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
# 2. ESTILIZAÇÃO CSS PERSONALIZADA (FCB THEME RESPONSIVO)
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

    /* Ticker Deslizante do Brasileirão */
    .ticker-wrap {
        width: 100%;
        background: linear-gradient(90deg, #0A1329 0%, #0F172A 50%, #0A1329 100%);
        border: 1px solid #1E293B;
        border-top: 2px solid #C8102E;
        overflow: hidden;
        white-space: nowrap;
        border-radius: 8px;
        margin-bottom: 20px;
        padding: 10px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    .ticker {
        display: inline-block;
        white-space: nowrap;
        padding-left: 100%;
        animation: marquee 35s linear infinite;
    }

    .ticker:hover {
        animation-play-state: paused;
    }

    .ticker-item {
        display: inline-block;
        padding: 0 25px;
        font-size: 13px;
        font-weight: 700;
        color: #94A3B8;
    }

    .ticker-item b {
        color: #FFFFFF;
    }

    @keyframes marquee {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
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

    /* Ajustes Mobile */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column !important;
            text-align: center !important;
            padding: 20px 15px !important;
            gap: 12px !important;
            border-left: none !important;
            border-top: 5px solid #C8102E !important;
        }

        .header-container img {
            height: 110px !important;
        }

        .header-title {
            font-size: 24px !important;
            letter-spacing: 1px !important;
        }

        .header-subtitle {
            font-size: 11px !important;
            letter-spacing: 1px !important;
        }

        .info-card, .pl-scoreboard-card {
            padding: 15px !important;
        }

        .fin-summary-box {
            flex-direction: column !important;
            gap: 15px !important;
        }
    }

    /* Cards Informativos Topo */
    .info-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .card-border-blue { border-left: 5px solid #38BDF8; }

    .card-tag {
        color: #38BDF8;
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

    /* Placar Estilo Premier League (PL) */
    .pl-scoreboard-card {
        background: linear-gradient(135deg, #38003c 0%, #110012 100%);
        border: 1px solid #00ff85;
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 20px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 0 15px rgba(0, 255, 133, 0.15);
        position: relative;
        overflow: hidden;
    }

    .pl-card-tag {
        color: #00ff85;
        font-size: 11px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .pl-scoreboard-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(10, 0, 15, 0.6);
        border-radius: 8px;
        padding: 8px 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(5px);
    }

    .pl-team-container {
        display: flex;
        align-items: center;
        gap: 10px;
        flex: 1;
    }

    .pl-team-container.right {
        justify-content: flex-end;
    }

    .pl-team-badge {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px currentColor;
    }
    .badge-bayern { background-color: #ef4444; color: #ef4444; }
    .badge-atletico { background-color: #38bdf8; color: #38bdf8; }

    .pl-team-name {
        color: #ffffff;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .pl-score-badge {
        background-color: #00ff85;
        color: #38003c;
        font-size: 16px;
        font-weight: 900;
        padding: 2px 10px;
        border-radius: 4px;
        min-width: 32px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 255, 133, 0.4);
    }

    .pl-draw-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 12px;
    }

    .pl-draw-badge {
        background-color: #64748B;
        color: #FFFFFF;
        font-size: 13px;
        font-weight: 900;
        padding: 2px 8px;
        border-radius: 4px;
        text-align: center;
    }

    .pl-draw-label {
        font-size: 9px;
        color: #94A3B8;
        font-weight: 700;
        margin-top: 2px;
    }

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

    /* Card Financeiro Rodapé */
    .financial-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-top: 4px solid #10B981;
        border-radius: 15px;
        padding: 25px;
        margin-top: 40px;
        margin-bottom: 10px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    .financial-title {
        color: #10B981;
        font-size: 14px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .fin-summary-box {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background-color: #070D18;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #1E293B;
    }
    .fin-item {
        text-align: center;
    }
    .fin-label {
        font-size: 11px;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .fin-value-green {
        font-size: 24px;
        font-weight: 900;
        color: #10B981;
    }
    .fin-value-red {
        font-size: 24px;
        font-weight: 900;
        color: #EF4444;
    }
    .fin-value-blue {
        font-size: 26px;
        font-weight: 900;
        color: #38BDF8;
    }

    /* Estilização dos Paga-Mensalidade */
    .paid-player-pill {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10B981;
        color: #10B981;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 13px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin: 4px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 3. TICKER DESLIZANTE DO BRASILEIRÃO
# ==========================================
@st.cache_data(ttl=1800)
def get_brasileirao_results():
    try:
        res = requests.get("https://api.cartolafc.globo.com/partidas", timeout=5).json()
        partidas = res.get("partidas", [])
        clubes = res.get("clubes", {})
        
        resultados = []
        for p in partidas:
            if p.get("placar_oficial_mandante") is not None and p.get("placar_oficial_visitante") is not None:
                m_id = str(p["clube_casa_id"])
                v_id = str(p["clube_visitante_id"])
                
                nome_m = clubes.get(m_id, {}).get("apelido", "Time")
                nome_v = clubes.get(v_id, {}).get("apelido", "Time")
                gols_m = p["placar_oficial_mandante"]
                gols_v = p["placar_oficial_visitante"]
                
                resultados.append(f"{nome_m} {gols_m} x {gols_v} {nome_v}")
        
        if resultados:
            return resultados
    except Exception:
        pass

    return [
        "Vitória 0 x 4 Palmeiras",
        "Coritiba 0 x 1 Cruzeiro",
        "Internacional 1 x 1 Flamengo",
        "Corinthians 0 x 0 Athletico-PR",
        "Mirassol 2 x 1 Remo",
        "Fluminense 0 x 0 Bahia",
        "Cruzeiro 0 x 1 Botafogo",
        "Palmeiras 1 x 2 Atlético-MG"
    ]

jogos_br = get_brasileirao_results()
items_html = "".join([f'<div class="ticker-item">⚽ <b>{jogo}</b></div> • ' for jogo in jogos_br])

ticker_html = (
    f'<div class="ticker-wrap">'
    f'<div class="ticker">'
    f'<span style="color: #F59E0B; font-weight: 900; padding: 0 15px;">🇧🇷 BRASILEIRÃO (ÚLTIMOS RESULTADOS):</span>'
    f'{items_html}'
    f'</div>'
    f'</div>'
)
st.markdown(ticker_html, unsafe_allow_html=True)

# ==========================================
# 4. CARREGAMENTO DAS PLANILHAS E CLIMA
# ==========================================
ID_PLANILHA_STATS = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"
URL_STATS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_STATS}/export?format=csv"

# Planilha de Vitórias e Empates
ID_PLANILHA_VITORIAS = "1e9VpoNzzqYZlD8JFJxWLQiWhNw4AaKiycauCZDxAas0"
GID_VITORIAS = "1092123094"
URL_VITORIAS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_VITORIAS}/export?format=csv&gid={GID_VITORIAS}"

ID_PLANILHA_JOGOS = "1Chjvd4vBarn9O4EgXWFnyMe5uIBgUsa4QCHIRr8C6Tk"
GID_JOGOS = "1092123094"
URL_JOGOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_JOGOS}/export?format=csv&gid={GID_JOGOS}"

# PLANILHA FINANCEIRA
ID_PLANILHA_FINANCEIRO = "14y1z7KtpNIHui1jpFZFCNXQMAvGziotMf5P9FxL2wdA"
GID_FINANCEIRO = "1092123094"
URL_FINANCEIRO = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_FINANCEIRO}/export?format=csv&gid={GID_FINANCEIRO}"

@st.cache_data(ttl=0)
def load_financial_data():
    try:
        df_fin = pd.read_csv(URL_FINANCEIRO, header=None)
        
        saldo = "R$ 239,00"
        gastos = "R$ 0,00"
        entradas = "R$ 40,00"
        jogadores_pagos = []
        
        for i in range(len(df_fin)):
            for j in range(len(df_fin.columns) - 1):
                cell_text = str(df_fin.iloc[i, j]).strip().lower()
                next_val = df_fin.iloc[i, j + 1]
                
                if pd.notna(next_val):
                    val_str = str(next_val).strip()
                    if "saldo actual" in cell_text or "saldo atual" in cell_text:
                        saldo = val_str if val_str.startswith("R$") else f"R$ {val_str}"
                    elif "gastos" in cell_text or "saidas" in cell_text or "saídas" in cell_text:
                        gastos = val_str if val_str.startswith("R$") else f"R$ {val_str}"
                    elif "entradas" in cell_text or "receitas" in cell_text:
                        entradas = val_str if val_str.startswith("R$") else f"R$ {val_str}"

        for i in range(len(df_fin)):
            cell_val = str(df_fin.iloc[i, 0]).strip().lower()
            if cell_val == "jogador":
                for k in range(i + 1, len(df_fin)):
                    nome_atleta = str(df_fin.iloc[k, 0]).strip()
                    if pd.isna(df_fin.iloc[k, 0]) or not nome_atleta or nome_atleta.lower() in ["saldo atual", "gastos", "entradas", "total"]:
                        continue
                    
                    status_pagamento = str(df_fin.iloc[k, 1]).strip() if len(df_fin.columns) > 1 else ""
                    if pd.notna(df_fin.iloc[k, 1]) and status_pagamento and status_pagamento.lower() != "nan":
                        jogadores_pagos.append({"nome": nome_atleta, "valor": status_pagamento})
                break
        
        if not jogadores_pagos:
            jogadores_pagos = [
                {"nome": "Caio", "valor": "R$ 20,00"},
                {"nome": "Emanoel Cjr", "valor": "R$ 20,00"}
            ]

        return entradas, gastos, saldo, jogadores_pagos
    except Exception:
        return "R$ 40,00", "R$ 0,00", "R$ 239,00", [
            {"nome": "Caio", "valor": "R$ 20,00"},
            {"nome": "Emanoel Cjr", "valor": "R$ 20,00"}
        ]

@st.cache_data(ttl=0)
def load_player_stats():
    df = pd.read_csv(URL_STATS, header=3)
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip()
    
    if "Time" in df.columns:
        df["Time"] = df["Time"].replace({"Vermelho": "Bayern de Madri", "Azul": "Atlético de Paris"})
    
    colunas_numericas = ["Gols", "Assistências", "Gols Contra", "Participações em Gols"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    if "Participações em Gols" not in df.columns and "Gols" in df.columns and "Assistências" in df.columns:
        df["Participações em Gols"] = df["Gols"] + df["Assistências"]

    return df

@st.cache_data(ttl=0)
def load_victories_stats():
    try:
        return pd.read_csv(URL_VITORIAS)
    except Exception:
        return pd.read_csv(f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_VITORIAS}/export?format=csv")

@st.cache_data(ttl=0)
def load_match_history():
    try:
        df_jogos = pd.read_csv(URL_JOGOS)
        df_jogos = df_jogos.dropna(how='all')
        df_jogos.columns = df_jogos.columns.str.strip()
        return df_jogos
    except Exception:
        return pd.read_csv(f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_JOGOS}/export?format=csv")

@st.cache_data(ttl=3600)
def get_next_saturday_weather():
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
# 5. CABEÇALHO OFICIAL
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
# 6. LEITURA DE VITÓRIAS E EMPATES (PLANILHA ID: 1e9VpoNzzqYZlD8JFJxWLQiWhNw4AaKiycauCZDxAas0)
# ==========================================
df_players = load_player_stats()
df_vitorias = load_victories_stats()

vitorias_bayern = 0
vitorias_atletico = 0
empates = 0

try:
    df_vitorias.columns = df_vitorias.columns.astype(str).str.strip()
    
    # Busca dinamicamente por formato de Linhas ou Colunas na planilha
    for idx, row in df_vitorias.iterrows():
        row_str = " ".join([str(val) for val in row.values]).lower()
        nums = [int(val) for val in row if str(val).isdigit()]
        
        if ("bayern" in row_str or "vermelho" in row_str) and nums:
            vitorias_bayern = nums[0]
        elif ("atlético" in row_str or "atletico" in row_str or "azul" in row_str) and nums:
            vitorias_atletico = nums[0]
        elif ("empate" in row_str or "empates" in row_str) and nums:
            empates = nums[0]

    # Mapeamento adicional para leitura via Cabeçalhos de Colunas
    for col in df_vitorias.columns:
        col_lower = col.lower()
        primeiro_valor = df_vitorias[col].dropna().iloc[0] if not df_vitorias[col].dropna().empty else None
        
        if primeiro_valor is not None and str(primeiro_valor).isdigit():
            val = int(primeiro_valor)
            if "bayern" in col_lower or "vermelho" in col_lower:
                vitorias_bayern = val
            elif "atlético" in col_lower or "atletico" in col_lower or "azul" in col_lower:
                vitorias_atletico = val
            elif "empate" in col_lower:
                empates = val
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

agora = datetime.now()
dias_ate_sabado = (5 - agora.weekday()) % 7
if dias_ate_sabado == 0 and agora.hour >= 16:
    dias_ate_sabado = 7

proximo_jogo = (agora + timedelta(days=dias_ate_sabado)).replace(hour=16, minute=0, second=0, microsecond=0)
tempo_restante = proximo_jogo - agora

dias = tempo_restante.days
horas, rem = divmod(tempo_restante.seconds, 3600)
minutos, segundos = divmod(rem, 60)

timer_html = (
    f'<div style="display: flex; gap: 8px; margin-top: 10px; align-items: center; justify-content: center;">'
    f'<span style="font-size: 11px; font-weight: 800; color: #38BDF8;">⏳ FALTAM:</span>'
    f'<div style="background: #0B1329; border: 1px solid #1E3A8A; border-radius: 6px; padding: 3px 8px; text-align: center;">'
    f'<span style="font-size: 13px; font-weight: 900; color: #FFF;">{dias:02d}d</span></div>'
    f'<div style="background: #0B1329; border: 1px solid #1E3A8A; border-radius: 6px; padding: 3px 8px; text-align: center;">'
    f'<span style="font-size: 13px; font-weight: 900; color: #FFF;">{horas:02d}h</span></div>'
    f'<div style="background: #0B1329; border: 1px solid #1E3A8A; border-radius: 6px; padding: 3px 8px; text-align: center;">'
    f'<span style="font-size: 13px; font-weight: 900; color: #FFF;">{minutos:02d}m</span></div>'
    f'</div>'
)

data_jogo = weather_info.get('data', '')
data_str = f" ({data_jogo})" if data_jogo else ""

col_jogo, col_placar = st.columns(2)

with col_jogo:
    card_jogo_html = (
        f'<div class="info-card card-border-blue" style="align-items: center; text-align: center;">'
        f'<div class="card-tag">📍 PRÓXIMO ENCONTRO</div>'
        f'<div class="card-main-text">Sábado{data_str} às 16:00 • Cambé - PR</div>'
        f'<div>{weather_html}</div>'
        f'{timer_html}'
        f'</div>'
    )
    st.markdown(card_jogo_html, unsafe_allow_html=True)

with col_placar:
    card_placar_html = (
        f'<div class="pl-scoreboard-card">'
        f'<div class="pl-card-tag">🏆 RETROSPECTO GERAL DOS CONFRONTOS</div>'
        f'<div class="pl-scoreboard-box">'
        f'<div class="pl-team-container">'
        f'<span class="pl-team-badge badge-bayern"></span>'
        f'<span class="pl-team-name">BAYERN</span>'
        f'<span class="pl-score-badge">{vitorias_bayern}</span>'
        f'</div>'
        f'<div class="pl-draw-container">'
        f'<span class="pl-draw-badge">{empates}</span>'
        f'<span class="pl-draw-label">EMPATES</span>'
        f'</div>'
        f'<div class="pl-team-container right">'
        f'<span class="pl-score-badge">{vitorias_atletico}</span>'
        f'<span class="pl-team-name">ATLÉTICO</span>'
        f'<span class="pl-team-badge badge-atletico"></span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_placar_html, unsafe_allow_html=True)

# ==========================================
# 7. CARDS DE DESTAQUES RÁPIDOS
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
    # 8. NAVEGAÇÃO POR PÍLULAS
    # ==========================================
    opcao_aba = st.radio(
        label="",
        options=[
            "🏆 Classificação Geral",
            "📅 Últimos Jogos FCB",
            "👥 Elenco dos Times",
            "⚔️ Duelo de Times",
            "🏅 Top 3 Artilharia"
        ],
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

    elif opcao_aba == "📅 Últimos Jogos FCB":
        st.subheader("📅 Resultados dos Últimos Encontros")
        df_historico_jogos = load_match_history()

        rename_cols = {}
        for col in df_historico_jogos.columns:
            if "azul" in col.lower():
                rename_cols[col] = "🔵 Atlético de Paris"
            elif "vermelho" in col.lower():
                rename_cols[col] = "🔴 Bayern de Madri"
            elif "gol" in col.lower():
                rename_cols[col] = "Gols ⚽"
            elif "assist" in col.lower():
                rename_cols[col] = "Assistências 🎯"

        df_historico_jogos = df_historico_jogos.rename(columns=rename_cols)

        cols_placar = [col for col in df_historico_jogos.columns if "Bayern" in col or "Atlético" in col]
        if cols_placar:
            df_historico_jogos = df_historico_jogos.dropna(subset=cols_placar, how="all")

        configs_colunas = {
            col: st.column_config.TextColumn(alignment="center") 
            for col in df_historico_jogos.columns
        }

        st.dataframe(
            df_historico_jogos,
            use_container_width=True,
            hide_index=True,
            column_config=configs_colunas
        )

    elif opcao_aba == "👥 Elenco dos Times":
        st.subheader("👥 Elenco Oficial dos Times")

        elenco_bayern = {
            "Goleiros": ["Vozinha"],
            "Zagueiros": ["Nilton", "Carlão (TCR)", "Camarão Sergipano"],
            "Laterais": ["Paulo Base", "Samuel", "Cezar", "Gledson"],
            "Meias": ["Cassiano", "Alessandro", "Mateus Rocha", "Diego (Lucas Lima)", "Cristiano", "Manoel"],
            "Atacantes": ["Nata", "Izaqui"]
        }

        elenco_atletico = {
            "Goleiros": ["Jonathan", "Matheus"],
            "Zagueiros": ["Gabigol", "Wellington", "Joel"],
            "Laterais": ["Caio", "Otero", "Cristoffer", "Jefferson"],
            "Meias": ["Ian", "Juel", "Gabriel"],
            "Atacantes": ["Tavinho", "P.H", "Maradona"]
        }

        col_bayern, col_atletico = st.columns(2)

        icones_pos = {
            "Goleiros": "🧤",
            "Zagueiros": "🛡️",
            "Laterais": "🏃‍♂️",
            "Meias": "🧠",
            "Atacantes": "⚡"
        }

        with col_bayern:
            st.markdown('<div class="roster-card"><div class="roster-header-vermelho"><h2>🔴 BAYERN DE MADRI</h2></div>', unsafe_allow_html=True)
            for pos, jogadores in elenco_bayern.items():
                st.markdown(f'<div class="pos-section-title">{icones_pos.get(pos, "⚽")} {pos}</div>', unsafe_allow_html=True)
                pills_html = "".join([f'<span class="player-pill">{j}</span>' for j in jogadores])
                st.markdown(f'<div>{pills_html}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_atletico:
            st.markdown('<div class="roster-card"><div class="roster-header-azul"><h2>🔵 ATLÉTICO DE PARIS</h2></div>', unsafe_allow_html=True)
            for pos, jogadores in elenco_atletico.items():
                st.markdown(f'<div class="pos-section-title">{icones_pos.get(pos, "⚽")} {pos}</div>', unsafe_allow_html=True)
                pills_html = "".join([f'<span class="player-pill">{j}</span>' for j in jogadores])
                st.markdown(f'<div>{pills_html}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif opcao_aba == "⚔️ Duelo de Times":
        st.subheader("⚔️ Comparativo: Bayern de Madri vs Atlético de Paris")
        if "Time" in df_players.columns:
            df_players["Time"] = df_players["Time"].replace({"Vermelho": "Bayern de Madri", "Azul": "Atlético de Paris"})
            stats_times = df_players.groupby("Time")[["Gols", "Assistências", "Gols Contra", "Participações em Gols"]].sum().reset_index()
            
            col_bayern, col_empate, col_atletico = st.columns([2, 1, 2])
            
            df_b = stats_times[stats_times["Time"] == "Bayern de Madri"]
            df_a = stats_times[stats_times["Time"] == "Atlético de Paris"]

            with col_bayern:
                gols_b = df_b["Gols"].values[0] if not df_b.empty else 0
                ast_b = df_b["Assistências"].values[0] if not df_b.empty else 0
                card_b = (
                    f'<div style="background-color: #3f0a14; border: 2px solid #C8102E; padding: 20px; border-radius: 12px; text-align: center;">'
                    f'<h2 style="color: #EF4444; margin: 0;">🔴 BAYERN</h2>'
                    f'<h1 style="color: #FFF; font-size: 38px; margin: 10px 0;">{vitorias_bayern} <span style="font-size: 16px;">VITÓRIAS</span></h1>'
                    f'<p style="color: #CBD5E1; font-weight: 600;">{gols_b} Gols | {ast_b} Assistências</p>'
                    f'</div>'
                )
                st.markdown(card_b, unsafe_allow_html=True)

            with col_empate:
                card_e = (
                    f'<div style="background-color: #1E293B; border: 2px solid #64748B; padding: 20px; border-radius: 12px; text-align: center;">'
                    f'<h2 style="color: #94A3B8; margin: 0;">🤝 EMPATES</h2>'
                    f'<h1 style="color: #FFF; font-size: 38px; margin: 10px 0;">{empates}</h1>'
                    f'<p style="color: #CBD5E1; font-weight: 600;">Igualdades</p>'
                    f'</div>'
                )
                st.markdown(card_e, unsafe_allow_html=True)

            with col_atletico:
                gols_a = df_a["Gols"].values[0] if not df_a.empty else 0
                ast_a = df_a["Assistências"].values[0] if not df_a.empty else 0
                card_a = (
                    f'<div style="background-color: #0A1E3F; border: 2px solid #38BDF8; padding: 20px; border-radius: 12px; text-align: center;">'
                    f'<h2 style="color: #38BDF8; margin: 0;">🔵 ATLÉTICO</h2>'
                    f'<h1 style="color: #FFF; font-size: 38px; margin: 10px 0;">{vitorias_atletico} <span style="font-size: 16px;">VITÓRIAS</span></h1>'
                    f'<p style="color: #CBD5E1; font-weight: 600;">{gols_a} Gols | {ast_a} Assistências</p>'
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

    # ==========================================
    # 9. SEÇÃO FINANCEIRA DO CLUBE (RODAPÉ)
    # ==========================================
    entradas, gastos, saldo_caixa, lista_pagos = load_financial_data()

    card_financeiro_html = f"""
    <div class="financial-card">
        <div class="financial-title">💰 PAINEL FINANCEIRO DO CLUBE</div>
        <div class="fin-summary-box">
            <div class="fin-item">
                <div class="fin-label">📈 Entradas (Mensalidades / Arrecadações)</div>
                <div class="fin-value-green">{entradas}</div>
            </div>
            <div class="fin-item">
                <div class="fin-label">📉 Gastos (Campo / Bolas / Coletes)</div>
                <div class="fin-value-red">{gastos}</div>
            </div>
            <div class="fin-item">
                <div class="fin-label">💵 Saldo Atual em Caixa</div>
                <div class="fin-value-blue">{saldo_caixa}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(card_financeiro_html), unsafe_allow_html=True)

    with st.expander("📋 Ver Atletas com Mensalidade Paga (Mês Atual)"):
        if lista_pagos:
            html_pagos = "".join([
                f'<div class="paid-player-pill">✅ <b>{atleta["nome"]}</b> ({atleta["valor"]})</div>'
                for atleta in lista_pagos
            ])
            st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">{html_pagos}</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum pagamento registrado até o momento para este mês.")

except Exception as e:
    st.error(f"Erro ao carregar dados das planilhas: {e}")
