import streamlit as st
import pandas as pd
import os
import base64
import requests
import re
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

    /* Ticker Deslizante do FCB */
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

    /* Banner do Cabeçalho Oficial (DESKTOP) */
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

    .header-logo {
        height: 140px;
        width: auto;
        object-fit: contain;
    }

    .header-text-container {
        display: flex;
        flex-direction: column;
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

    /* AJUSTE EXCLUSIVO PARA SMARTPHONES (MOBILE) */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column !important;
            align-items: center !important;
            text-align: center !important;
            padding: 20px 15px !important;
            gap: 15px !important;
        }

        .header-logo {
            height: 110px !important;
            margin-bottom: 5px !important;
        }

        .header-text-container {
            align-items: center !important;
            text-align: center !important;
        }

        .header-title {
            font-size: 26px !important;
        }

        .header-subtitle {
            font-size: 12px !important;
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
    }

    .pl-card-tag {
        color: #00ff85;
        font-size: 11px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .pl-scoreboard-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(10, 0, 15, 0.6);
        border-radius: 8px;
        padding: 8px 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
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
    }
    .badge-bayern { background-color: #ef4444; }
    .badge-atletico { background-color: #38bdf8; }

    .pl-team-name {
        color: #ffffff;
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
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
    }

    .pl-draw-label {
        font-size: 9px;
        color: #94A3B8;
        font-weight: 700;
        margin-top: 2px;
    }

    /* Subtexto do Último Resultado no Card */
    .pl-last-result {
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px dashed rgba(255, 255, 255, 0.15);
        text-align: center;
        font-size: 11px;
        color: #94A3B8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pl-last-result b {
        color: #00ff85;
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

    /* ESTILO DO CAMPO DE FUTEBOL TÁTICO */
    .pitch-container {
        position: relative;
        width: 100%;
        min-height: 580px;
        background: repeating-linear-gradient(
            0deg,
            #1e5128,
            #1e5128 40px,
            #194320 40px,
            #194320 80px
        );
        border: 3px solid #ffffff;
        border-radius: 12px;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.6), 0 8px 24px rgba(0,0,0,0.5);
        display: flex;
        flex-direction: column-reverse; /* Inverte para Goleiro ficar na base e Atacantes no topo */
        justify-content: space-around;
        align-items: center;
        padding: 25px 10px;
        overflow: hidden;
        margin-bottom: 20px;
    }

    /* Linhas do Campo */
    .pitch-line-center {
        position: absolute;
        top: 50%;
        left: 0;
        width: 100%;
        height: 2px;
        background-color: rgba(255, 255, 255, 0.4);
        pointer-events: none;
    }

    .pitch-circle-center {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 110px;
        height: 110px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        pointer-events: none;
    }

    .pitch-box-bottom {
        position: absolute;
        bottom: 0;
        left: 50%;
        width: 180px;
        height: 70px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-bottom: none;
        transform: translateX(-50%);
        pointer-events: none;
    }

    .pitch-box-top {
        position: absolute;
        top: 0;
        left: 50%;
        width: 180px;
        height: 70px;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-top: none;
        transform: translateX(-50%);
        pointer-events: none;
    }

    .pitch-row {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        width: 100%;
    }

    /* Pílula Tática de Jogador */
    .pitch-player {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 20px;
        padding: 5px 12px;
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        backdrop-filter: blur(4px);
    }

    .pitch-badge-bayern {
        background: #C8102E;
        color: #FFFFFF;
        padding: 2px 7px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 900;
    }

    .pitch-badge-atletico {
        background: #0284C7;
        color: #FFFFFF;
        padding: 2px 7px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 900;
    }

    .roster-card-header {
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-weight: 900;
    }

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

    .unpaid-player-pill {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid #EF4444;
        color: #EF4444;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 13px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin: 4px;
    }

    .pix-key-box {
        background-color: #0F172A;
        border: 1px dashed #10B981;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 10px;
        color: #F1F5F9;
        font-size: 14px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# 3. CARREGAMENTO DAS PLANILHAS E CLIMA
# ==========================================
ID_PLANILHA_STATS = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"
URL_STATS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_STATS}/export?format=csv"

ID_PLANILHA_VITORIAS = "1e9VpoNzzqYZlD8JFJxWLQiWhNw4AaKiycauCZDxAas0"
GID_VITORIAS = "1092123094"
URL_VITORIAS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_VITORIAS}/export?format=csv&gid={GID_VITORIAS}"

ID_PLANILHA_JOGOS = "1Chjvd4vBarn9O4EgXWFnyMe5uIBgUsa4QCHIRr8C6Tk"
GID_JOGOS = "1092123094"
URL_JOGOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_JOGOS}/export?format=csv&gid={GID_JOGOS}"

ID_PLANILHA_FINANCEIRO = "14y1z7KtpNIHui1jpFZFCNXQMAvGziotMf5P9FxL2wdA"
GID_FINANCEIRO = "1092123094"
URL_FINANCEIRO = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_FINANCEIRO}/export?format=csv&gid={GID_FINANCEIRO}"

ID_PLANILHA_GOLS = "1xrThBr83ehD7yPtPzaknTXiHtccFIaeQmm60HPdJXCA"
URL_GOLS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_GOLS}/export?format=csv"

@st.cache_data(ttl=60)
def load_match_history():
    try:
        df_jogos = pd.read_csv(URL_JOGOS)
        df_jogos = df_jogos.dropna(how='all')
        df_jogos.columns = df_jogos.columns.str.strip()
        return df_jogos
    except Exception:
        return pd.read_csv(f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_JOGOS}/export?format=csv")

# ==========================================
# TICKER DESLIZANTE DE JOGOS FCB
# ==========================================
@st.cache_data(ttl=60)
def get_fcb_match_results():
    try:
        df_jogos = load_match_history()
        if df_jogos.empty:
            return ["Aguardando registro de jogos do FCB..."]

        col_bayern = [c for c in df_jogos.columns if "vermelho" in c.lower() or "bayern" in c.lower()]
        col_atletico = [c for c in df_jogos.columns if "azul" in c.lower() or "atlético" in c.lower() or "atletico" in c.lower()]
        col_data = [c for c in df_jogos.columns if "data" in c.lower() or "rodada" in c.lower() or "jogo" in c.lower()]

        if not col_bayern or not col_atletico:
            return ["Formato de planilha não reconhecido."]

        resultados = []
        df_validos = df_jogos.dropna(subset=[col_bayern[0], col_atletico[0]], how="all")

        for _, row in df_validos.iterrows():
            gols_b_raw = row[col_bayern[0]]
            gols_a_raw = row[col_atletico[0]]

            if pd.notna(gols_b_raw) and pd.notna(gols_a_raw):
                try:
                    gols_b = int(float(gols_b_raw))
                    gols_a = int(float(gols_a_raw))
                    
                    data_info = ""
                    if col_data and pd.notna(row[col_data[0]]):
                        data_info = f" ({str(row[col_data[0]]).strip()})"
                    
                    resultados.append(f"Bayern {gols_b} x {gols_a} Atlético{data_info}")
                except ValueError:
                    continue

        if resultados:
            return resultados[::-1]
    except Exception:
        pass

    return ["Nenhum jogo registrado até o momento."]

jogos_fcb_ticker = get_fcb_match_results()
items_html = "".join([f'<div class="ticker-item">⚽ <b>{jogo}</b></div> • ' for jogo in jogos_fcb_ticker])

ticker_html = (
    f'<div class="ticker-wrap">'
    f'<div class="ticker">'
    f'<span style="color: #38BDF8; font-weight: 900; padding: 0 15px;">🛡️ RESULTADOS RECENTES FCB:</span>'
    f'{items_html}'
    f'</div>'
    f'</div>'
)
st.markdown(ticker_html, unsafe_allow_html=True)

# ==========================================
# OUTROS CARREGAMENTOS DE DADOS
# ==========================================
@st.cache_data(ttl=60)
def load_financial_data():
    try:
        df_fin = pd.read_csv(URL_FINANCEIRO, header=None)
        
        saldo = "R$ 0,00"
        gastos = "R$ 0,00"
        entradas = "R$ 0,00"
        
        jogadores_pagos = []
        jogadores_pendentes = []
        lista_gastos_detalhada = []
        
        if len(df_fin) > 1 and len(df_fin.columns) > 1 and pd.notna(df_fin.iloc[1, 1]):
            val_b2 = str(df_fin.iloc[1, 1]).strip()
            gastos = val_b2 if val_b2.startswith("R$") else f"R$ {val_b2}"

        for i in range(len(df_fin)):
            for j in range(len(df_fin.columns) - 1):
                cell_text = str(df_fin.iloc[i, j]).strip().lower()
                next_val = df_fin.iloc[i, j + 1]
                
                if pd.notna(next_val):
                    val_str = str(next_val).strip()
                    if "saldo actual" in cell_text or "saldo atual" in cell_text:
                        saldo = val_str if val_str.startswith("R$") else f"R$ {val_str}"
                    elif "entradas" in cell_text or "receitas" in cell_text or "arrecadacoes" in cell_text or "arrecadações" in cell_text:
                        entradas = val_str if val_str.startswith("R$") else f"R$ {val_str}"

        for i in range(len(df_fin)):
            cell_val = str(df_fin.iloc[i, 0]).strip().lower()
            if cell_val == "jogador" or "jogador" in cell_val:
                for k in range(i + 1, len(df_fin)):
                    nome_atleta = str(df_fin.iloc[k, 0]).strip()
                    if pd.isna(df_fin.iloc[k, 0]) or not nome_atleta or nome_atleta.lower() in ["saldo atual", "gastos", "entradas", "total", "nan"]:
                        continue
                    
                    status_val = str(df_fin.iloc[k, 1]).strip() if len(df_fin.columns) > 1 else ""
                    
                    if pd.notna(df_fin.iloc[k, 1]) and status_val and status_val.lower() not in ["nan", "não", "nao", "pendente", "0", "r$ 0,00"]:
                        valor_pago = status_val if status_val.startswith("R$") else f"R$ {status_val}"
                        jogadores_pagos.append({"nome": nome_atleta, "valor": valor_pago})
                    else:
                        jogadores_pendentes.append({"nome": nome_atleta, "status": "Pendente"})
                break

        if len(df_fin.columns) >= 8:
            for i in range(len(df_fin)):
                item_gasto = df_fin.iloc[i, 7]
                if pd.notna(item_gasto):
                    item_str = str(item_gasto).strip()
                    if item_str.lower() not in ["gastos", "descrição", "tipo de gasto", "nan"]:
                        val_gasto = str(df_fin.iloc[i, 8]).strip() if len(df_fin.columns) > 8 and pd.notna(df_fin.iloc[i, 8]) else ""
                        lista_gastos_detalhada.append({"descricao": item_str, "valor": val_gasto})

        return entradas, gastos, saldo, jogadores_pagos, jogadores_pendentes, lista_gastos_detalhada

    except Exception:
        return "R$ 80,00", "R$ 0,00", "R$ 168,44", [], [], []

@st.cache_data(ttl=60)
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

@st.cache_data(ttl=60)
def load_victories_stats():
    try:
        return pd.read_csv(URL_VITORIAS)
    except Exception:
        return pd.read_csv(f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_VITORIAS}/export?format=csv")

@st.cache_data(ttl=60)
def load_gols_rodada():
    try:
        df_gols = pd.read_csv(URL_GOLS)
        df_gols = df_gols.dropna(how='all')
        df_gols.columns = df_gols.columns.astype(str).str.strip()
        return df_gols
    except Exception:
        return pd.DataFrame()

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
                icon = "⛅ Parcialmente Nublado" if wcode in [1, 2] else "☁ Nublado"
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
# 5. CABEÇALHO OFICIAL (COM SUPORTE RESPONSIVO)
# ==========================================
try:
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    logo_path = os.path.join(base_dir, "logo.png")
    if os.path.exists(logo_path):
        logo_base64 = get_base64_of_bin_file(logo_path)
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="header-logo">'
    else:
        logo_html = '<h1 style="margin:0; font-size: 70px;">🛡️</h1>'
except Exception:
    logo_html = '<h1 style="margin:0; font-size: 70px;">🛡️</h1>'

header_code = f"""
<div class="header-container">
    <div>{logo_html}</div>
    <div class="header-text-container">
        <h1 class="header-title">FUTEBOL CASTELO BRANCO</h1>
        <p class="header-subtitle">PAINEL OFICIAL DE ESTATÍSTICAS • TEMPORADA 2026</p>
    </div>
</div>
"""
st.markdown(header_code, unsafe_allow_html=True)

# ==========================================
# 6. CARDS SUPERIORES COM TEMPORIZADOR E PLACAR COMPLETO
# ==========================================
df_players = load_player_stats()
df_vitorias = load_victories_stats()
df_jogos_fcb = load_match_history()

vitorias_bayern = 0
vitorias_atletico = 0
empates = 0

try:
    df_vitorias.columns = df_vitorias.columns.astype(str).str.strip()
    
    for idx, row in df_vitorias.iterrows():
        row_str = " ".join([str(val) for val in row.values]).lower()
        nums = [int(val) for val in row if str(val).isdigit()]
        
        if ("bayern" in row_str or "vermelho" in row_str) and nums:
            vitorias_bayern = nums[0]
        elif ("atlético" in row_str or "atletico" in row_str or "azul" in row_str) and nums:
            vitorias_atletico = nums[0]
        elif ("empate" in row_str or "empates" in row_str) and nums:
            empates = nums[0]

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

texto_ultimo_jogo = "Sem registros recentes"
try:
    if not df_jogos_fcb.empty:
        col_bayern = [c for c in df_jogos_fcb.columns if "vermelho" in c.lower() or "bayern" in c.lower()]
        col_atletico = [c for c in df_jogos_fcb.columns if "azul" in c.lower() or "atlético" in c.lower() or "atletico" in c.lower()]
        
        if col_bayern and col_atletico:
            df_validos = df_jogos_fcb.dropna(subset=[col_bayern[0], col_atletico[0]], how="all")
            if not df_validos.empty:
                ultimo_reg = df_validos.iloc[-1]
                gols_b = int(pd.to_numeric(ultimo_reg[col_bayern[0]], errors='coerce') or 0)
                gols_a = int(pd.to_numeric(ultimo_reg[col_atletico[0]], errors='coerce') or 0)
                
                col_data = [c for c in df_jogos_fcb.columns if "data" in c.lower() or "rodada" in c.lower() or "jogo" in c.lower()]
                info_data = f" ({str(ultimo_reg[col_data[0]]).strip()})" if col_data and pd.notna(ultimo_reg[col_data[0]]) else ""
                
                texto_ultimo_jogo = f"Bayern <b>{gols_b} x {gols_a}</b> Atlético{info_data}"
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
        f'<div class="pl-last-result">⚡ ÚLTIMO CONFRONTO: {texto_ultimo_jogo}</div>'
        f'</div>'
    )
    st.markdown(card_placar_html, unsafe_allow_html=True)

# ==========================================
# 7. CARDS DE DESTAQUES RÁPIDOS
# ==========================================
artilheiro = df_players.sort_values(by="Gols", ascending=False).iloc[0] if not df_players.empty else None
garcom = df_players.sort_values(by="Assistências", ascending=False).iloc[0] if not df_players.empty else None
lider_participacoes = df_players.sort_values(by="Participações em Gols", ascending=False).iloc[0] if not df_players.empty else None

c1, c2, c3, c4 = st.columns(4)

with c1:
    total_g = df_players["Gols"].sum() if not df_players.empty else 0
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

    st.dataframe(
        df_historico_jogos,
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------
    # SEÇÃO DE VÍDEOS PULL DIRETO DA PLANILHA GOLS_RODADA
    # ------------------------------------------
    st.markdown("<br><hr style='border:1px solid #1E293B;'><br>", unsafe_allow_html=True)
    
    col_tit, col_btn = st.columns([3, 1])
    with col_tit:
        st.markdown("### 🎥 Gols e Melhores Momentos da Rodada")
    with col_btn:
        if st.button("🔄 Atualizar Vídeos", use_container_width=True):
            load_gols_rodada.clear()
            st.rerun()

    df_gols = load_gols_rodada()

    def extrair_id_drive(texto):
        if pd.isna(texto) or not str(texto).strip():
            return None
        texto_str = str(texto).strip()
        ids_d = re.findall(r'/d/([a-zA-Z0-9_-]{25,50})', texto_str)
        if ids_d:
            return ids_d[0]
        ids_id = re.findall(r'id=([a-zA-Z0-9_-]{25,50})', texto_str)
        if ids_id:
            return ids_id[0]
        if len(texto_str) >= 25 and len(texto_str) <= 50 and '/' not in texto_str:
            return texto_str
        return None

    videos_encontrados = []
    if not df_gols.empty:
        col_titulo = [c for c in df_gols.columns if "titulo" in c.lower() or "título" in c.lower() or "nome" in c.lower() or "lance" in c.lower()]
        col_link = [c for c in df_gols.columns if "link" in c.lower() or "video" in c.lower() or "vídeo" in c.lower() or "url" in c.lower() or "drive" in c.lower()]

        c_tit = col_titulo[0] if col_titulo else df_gols.columns[0]
        c_lnk = col_link[0] if col_link else (df_gols.columns[1] if len(df_gols.columns) > 1 else df_gols.columns[0])

        for idx, row in df_gols.iterrows():
            f_id = extrair_id_drive(row[c_lnk])
            if f_id:
                titulo = str(row[c_tit]).strip() if pd.notna(row[c_tit]) else f"⚽ Lance {idx+1}"
                videos_encontrados.append({"titulo": titulo, "id": f_id})

    if videos_encontrados:
        for i in range(0, len(videos_encontrados), 2):
            cols = st.columns(2)
            
            with cols[0]:
                vid1 = videos_encontrados[i]
                st.markdown(f"**⚽ {vid1['titulo']}**")
                embed_code1 = f"""
                <iframe src="https://drive.google.com/file/d/{vid1['id']}/preview" 
                        width="100%" 
                        height="320" 
                        allow="autoplay; fullscreen" 
                        style="border:1px solid #1E293B; border-radius:12px; background-color:#000;">
                </iframe>
                """
                st.components.v1.html(embed_code1, height=330)
                st.link_button("▶ Abrir / Assistir Vídeo", f"https://drive.google.com/file/d/{vid1['id']}/view", use_container_width=True)

            if i + 1 < len(videos_encontrados):
                with cols[1]:
                    vid2 = videos_encontrados[i + 1]
                    st.markdown(f"**⚽ {vid2['titulo']}**")
                    embed_code2 = f"""
                    <iframe src="https://drive.google.com/file/d/{vid2['id']}/preview" 
                            width="100%" 
                            height="320" 
                            allow="autoplay; fullscreen" 
                            style="border:1px solid #1E293B; border-radius:12px; background-color:#000;">
                    </iframe>
                    """
                    st.components.v1.html(embed_code2, height=330)
                    st.link_button("▶️ Abrir / Assistir Vídeo", f"https://drive.google.com/file/d/{vid2['id']}/view", use_container_width=True)
    else:
        st.info("Nenhum vídeo cadastrado na planilha 'gols_rodada' até o momento.")

elif opcao_aba == "👥 Elenco dos Times":
    st.subheader("👥 Disposição Tática nos Campos")

    if "elenco_jogadores" not in st.session_state:
        st.session_state.elenco_jogadores = pd.DataFrame([
            # BAYERN DE MADRI
            {"Jogador": "Vozinha", "Numero": 1, "Time": "🔴 Bayern de Madri", "Posição": "Goleiros"},
            {"Jogador": "Nilton", "Numero": 3, "Time": "🔴 Bayern de Madri", "Posição": "Zagueiros"},
            {"Jogador": "Carlão (TCR)", "Numero": 4, "Time": "🔴 Bayern de Madri", "Posição": "Zagueiros"},
            {"Jogador": "Paulo Base", "Numero": 2, "Time": "🔴 Bayern de Madri", "Posição": "Laterais"},
            {"Jogador": "Cezar", "Numero": 13, "Time": "🔴 Bayern de Madri", "Posição": "Laterais"},
            {"Jogador": "Gledson", "Numero": 14, "Time": "🔴 Bayern de Madri", "Posição": "Laterais"},
            {"Jogador": "Cláudio", "Numero": 69, "Time": "🔴 Bayern de Madri", "Posição": "Laterais"},
            {"Jogador": "Camarão Sergipano", "Numero": 70, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Cassiano", "Numero": 33, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Alessandro", "Numero": 31, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Mateus Rocha", "Numero": 7, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Diego (Lucas Lima)", "Numero": 20, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Cristiano", "Numero": 10, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Manoel", "Numero": 26, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Wesley", "Numero": 30, "Time": "🔴 Bayern de Madri", "Posição": "Meias"},
            {"Jogador": "Nata", "Numero": 99, "Time": "🔴 Bayern de Madri", "Posição": "Atacantes"},
            {"Jogador": "Izaqui", "Numero": 9, "Time": "🔴 Bayern de Madri", "Posição": "Atacantes"},
            # ATLÉTICO DE PARIS
            {"Jogador": "Jonathan", "Numero": 1, "Time": "🔵 Atlético de Paris", "Posição": "Goleiros"},
            {"Jogador": "Mateus Ar Condicionado", "Numero": 22, "Time": "🔵 Atlético de Paris", "Posição": "Goleiros"},
            {"Jogador": "Wellington", "Numero": 99, "Time": "🔵 Atlético de Paris", "Posição": "Zagueiros"},
            {"Jogador": "P.H", "Numero": 31, "Time": "🔵 Atlético de Paris", "Posição": "Zagueiros"},
            {"Jogador": "Samuel", "Numero": 13, "Time": "🔵 Atlético de Paris", "Posição": "Laterais"},
            {"Jogador": "Otero", "Numero": 17, "Time": "🔵 Atlético de Paris", "Posição": "Laterais"},
            {"Jogador": "Cristoffer", "Numero": 2, "Time": "🔵 Atlético de Paris", "Posição": "Laterais"},
            {"Jogador": "Jefferson", "Numero": 23, "Time": "🔵 Atlético de Paris", "Posição": "Laterais"},
            {"Jogador": "Ian", "Numero": 30, "Time": "🔵 Atlético de Paris", "Posição": "Meias"},
            {"Jogador": "Juel", "Numero": 8, "Time": "🔵 Atlético de Paris", "Posição": "Meias"},
            {"Jogador": "Gabriel", "Numero": 26, "Time": "🔵 Atlético de Paris", "Posição": "Meias"},
            {"Jogador": "Caio", "Numero": 7, "Time": "🔵 Atlético de Paris", "Posição": "Meias"},
            {"Jogador": "Renan", "Numero": 20, "Time": "🔵 Atlético de Paris", "Posição": "Meias"},
            {"Jogador": "Mateus Barbosa", "Numero": 10, "Time": "🔵 Atlético de Paris", "Posição": "Meias"},
            {"Jogador": "Tavinho", "Numero": 9, "Time": "🔵 Atlético de Paris", "Posição": "Atacantes"},
            {"Jogador": "Maradona", "Numero": 19, "Time": "🔵 Atlético de Paris", "Posição": "Atacantes"}
        ])

    if "Numero" not in st.session_state.elenco_jogadores.columns:
        st.session_state.elenco_jogadores["Numero"] = 10

    with st.expander("⚙️ **Gerenciar Atletas (Adicionar, Editar e Excluir)**", expanded=False):
        tab_add, tab_edit, tab_del = st.tabs(["➕ Cadastrar Atleta", "✏️ Editar Atleta", "🗑️ Excluir Atleta"])
        
        opcoes_times = ["🔴 Bayern de Madri", "🔵 Atlético de Paris"]
        opcoes_posicoes = ["Goleiros", "Zagueiros", "Laterais", "Meias", "Atacantes"]

        # TAB 1: CADASTRAR JOGADOR
        with tab_add:
            c_add1, c_add2, c_add3, c_add4 = st.columns([2, 1, 1, 1])
            with c_add1:
                novo_nome = st.text_input("Nome do Novo Atleta:", key="add_nome")
            with c_add2:
                novo_num = st.number_input("Nº da Camisa:", min_value=1, max_value=99, value=10, step=1, key="add_num")
            with c_add3:
                add_time = st.selectbox("Time:", opcoes_times, key="add_time")
            with c_add4:
                add_pos = st.selectbox("Posição:", opcoes_posicoes, key="add_pos")
                
            if st.button("➕ Adicionar Atleta", use_container_width=True):
                nome_limpo = novo_nome.strip()
                if nome_limpo:
                    ja_existe = st.session_state.elenco_jogadores["Jogador"].str.lower() == nome_limpo.lower()
                    if ja_existe.any():
                        st.error(f"❌ O atleta '{nome_limpo}' já está cadastrado no elenco!")
                    else:
                        novo_reg = pd.DataFrame([{"Jogador": nome_limpo, "Numero": int(novo_num), "Time": add_time, "Posição": add_pos}])
                        st.session_state.elenco_jogadores = pd.concat([st.session_state.elenco_jogadores, novo_reg], ignore_index=True)
                        st.success(f"✅ Atleta {nome_limpo} (#{novo_num}) adicionado com sucesso ao {add_time}!")
                        st.rerun()
                else:
                    st.warning("⚠️ Digite um nome para cadastrar o atleta.")

        # TAB 2: EDITAR JOGADOR
        with tab_edit:
            todos_jogadores = sorted(st.session_state.elenco_jogadores["Jogador"].tolist()) if not st.session_state.elenco_jogadores.empty else []
            if todos_jogadores:
                c_edit1, c_edit2, c_edit3, c_edit4 = st.columns([2, 1, 1, 1])
                with c_edit1:
                    jogador_sel = st.selectbox("Selecione o Atleta:", todos_jogadores, key="edit_sel")
                    
                dados_atuais = st.session_state.elenco_jogadores[st.session_state.elenco_jogadores["Jogador"] == jogador_sel].iloc[0]
                num_atual = int(dados_atuais["Numero"]) if "Numero" in dados_atuais and pd.notna(dados_atuais["Numero"]) else 10
                idx_time = opcoes_times.index(dados_atuais["Time"]) if dados_atuais["Time"] in opcoes_times else 0
                idx_pos = opcoes_posicoes.index(dados_atuais["Posição"]) if dados_atuais["Posição"] in opcoes_posicoes else 0
                
                with c_edit2:
                    edit_num = st.number_input("Nº Camisa:", min_value=1, max_value=99, value=num_atual, step=1, key="edit_num")
                with c_edit3:
                    edit_time = st.selectbox("Novo Time:", opcoes_times, index=idx_time, key="edit_time")
                with c_edit4:
                    edit_pos = st.selectbox("Nova Posição:", opcoes_posicoes, index=idx_pos, key="edit_pos")

                if st.button("💾 Salvar Alteração", use_container_width=True):
                    mask = st.session_state.elenco_jogadores["Jogador"] == jogador_sel
                    st.session_state.elenco_jogadores.loc[mask, "Numero"] = int(edit_num)
                    st.session_state.elenco_jogadores.loc[mask, "Time"] = edit_time
                    st.session_state.elenco_jogadores.loc[mask, "Posição"] = edit_pos
                    st.success(f"✅ {jogador_sel} (#{edit_num}) atualizado com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhum atleta cadastrado para editar.")

        # TAB 3: EXCLUIR JOGADOR
        with tab_del:
            todos_jogadores = sorted(st.session_state.elenco_jogadores["Jogador"].tolist()) if not st.session_state.elenco_jogadores.empty else []
            if todos_jogadores:
                col_del1, col_del2 = st.columns([2, 1])
                with col_del1:
                    jogador_del = st.selectbox("Selecione o Atleta para Remover:", todos_jogadores, key="del_sel")
                with col_del2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️ Excluir Atleta", type="primary", use_container_width=True):
                        st.session_state.elenco_jogadores = st.session_state.elenco_jogadores[
                            st.session_state.elenco_jogadores["Jogador"] != jogador_del
                        ].reset_index(drop=True)
                        st.success(f"🗑️ Atleta {jogador_del} removido com sucesso!")
                        st.rerun()
            else:
                st.info("Nenhum atleta cadastrado para excluir.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------
    # FUNÇÃO PARA GERAR O CAMPO DE FUTEBOL HTML
    # ------------------------------------------
    def renderizar_campo_tatico(df_team, badge_class):
        posicoes_ordem = ["Goleiros", "Zagueiros", "Laterais", "Meias", "Atacantes"]
        icones_pos = {"Goleiros": "🧤", "Zagueiros": "🛡️", "Laterais": "🏃‍♂️", "Meias": "🧠", "Atacantes": "⚡"}

        rows_html = ""
        for pos in posicoes_ordem:
            df_pos = df_team[df_team["Posição"] == pos]
            if not df_pos.empty:
                players_html = ""
                for _, row in df_pos.iterrows():
                    num = int(row["Numero"]) if pd.notna(row["Numero"]) else 0
                    nome = row["Jogador"]
                    players_html += f"""
                    <div class="pitch-player">
                        <span class="{badge_class}">#{num}</span>
                        <span>{nome}</span>
                    </div>
                    """
                rows_html += f'<div class="pitch-row">{players_html}</div>'

        field_html = f"""
        <div class="pitch-container">
            <div class="pitch-line-center"></div>
            <div class="pitch-circle-center"></div>
            <div class="pitch-box-bottom"></div>
            <div class="pitch-box-top"></div>
            {rows_html}
        </div>
        """
        return field_html

    df_elenco = st.session_state.elenco_jogadores
    col_bayern, col_atletico = st.columns(2)

    with col_bayern:
        st.markdown('<div class="roster-card-header" style="background:#3f0a14; border:2px solid #C8102E; color:#EF4444;">🔴 BAYERN DE MADRI</div>', unsafe_allow_html=True)
        df_bayern = df_elenco[df_elenco["Time"] == "🔴 Bayern de Madri"]
        html_bayern = renderizar_campo_tatico(df_bayern, "pitch-badge-bayern")
        st.markdown(html_bayern, unsafe_allow_html=True)

    with col_atletico:
        st.markdown('<div class="roster-card-header" style="background:#0A1E3F; border:2px solid #38BDF8; color:#38BDF8;">🔵 ATLÉTICO DE PARIS</div>', unsafe_allow_html=True)
        df_atletico = df_elenco[df_elenco["Time"] == "🔵 Atlético de Paris"]
        html_atletico = renderizar_campo_tatico(df_atletico, "pitch-badge-atletico")
        st.markdown(html_atletico, unsafe_allow_html=True)

elif opcao_aba == "⚔️ Duelo de Times":
    st.subheader("⚔️ Comparativo: Bayern de Madri vs Atlético de Paris")
    if "Time" in df_players.columns:
        df_players["Time"] = df_players["Time"].replace({"Vermelho": "Bayern de Madri", "Azul": "Atlético de Paris"})
        stats_times = df_players.groupby("Time")[["Gols", "Assistências", "Gols Contra", "Participações em Gols"]].sum().reset_index()
        
        col_bayern, col_empate, col_atletico = st.columns([1, 1, 1])
        df_b = stats_times[stats_times["Time"] == "Bayern de Madri"]
        df_a = stats_times[stats_times["Time"] == "Atlético de Paris"]

        card_style_base = "height: 180px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; padding: 20px; border-radius: 12px; text-align: center;"

        with col_bayern:
            gols_b = df_b["Gols"].values[0] if not df_b.empty else 0
            ast_b = df_b["Assistências"].values[0] if not df_b.empty else 0
            card_b = (
                f'<div style="background-color: #3f0a14; border: 2px solid #C8102E; {card_style_base}">'
                f'<h2 style="color: #EF4444; margin: 0; font-size: 20px;">🔴 BAYERN</h2>'
                f'<h1 style="color: #FFF; font-size: 36px; margin: 0;">{vitorias_bayern} <span style="font-size: 14px;">VITÓRIAS</span></h1>'
                f'<p style="color: #CBD5E1; font-weight: 600; margin: 0; font-size: 13px;">{gols_b} Gols | {ast_b} Assistências</p>'
                f'</div>'
            )
            st.markdown(card_b, unsafe_allow_html=True)

        with col_empate:
            card_e = (
                f'<div style="background-color: #1E293B; border: 2px solid #64748B; {card_style_base}">'
                f'<h2 style="color: #94A3B8; margin: 0; font-size: 20px;">🤝 EMPATES</h2>'
                f'<h1 style="color: #FFF; font-size: 36px; margin: 0;">{empates}</h1>'
                f'<p style="color: #CBD5E1; font-weight: 600; margin: 0; font-size: 13px;">Igualdades no Retrospecto</p>'
                f'</div>'
            )
            st.markdown(card_e, unsafe_allow_html=True)

        with col_atletico:
            gols_a = df_a["Gols"].values[0] if not df_a.empty else 0
            ast_a = df_a["Assistências"].values[0] if not df_a.empty else 0
            card_a = (
                f'<div style="background-color: #0A1E3F; border: 2px solid #38BDF8; {card_style_base}">'
                f'<h2 style="color: #38BDF8; margin: 0; font-size: 20px;">🔵 ATLÉTICO</h2>'
                f'<h1 style="color: #FFF; font-size: 36px; margin: 0;">{vitorias_atletico} <span style="font-size: 16px;">VITÓRIAS</span></h1>'
                f'<p style="color: #CBD5E1; font-weight: 600; margin: 0; font-size: 13px;">{gols_a} Gols | {ast_a} Assistências</p>'
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
st.markdown("<br><hr style='border:1px solid #1E293B;'><br>", unsafe_allow_html=True)
st.subheader("💰 PAINEL FINANCEIRO DO CLUBE")

entradas, gastos_b2, saldo_caixa, lista_pagos, lista_pendentes, detalhe_gastos = load_financial_data()

# Cards de Resumo Financeiro
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div style="background:#070D18; border:1px solid #1E293B; border-radius:10px; padding:15px; text-align:center;"><div style="color:#94A3B8; font-size:12px; font-weight:700;">📈 ENTRADAS (MENSALIDADES)</div><div style="color:#10B981; font-size:26px; font-weight:900; margin-top:5px;">{entradas}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div style="background:#070D18; border:1px solid #1E293B; border-radius:10px; padding:15px; text-align:center;"><div style="color:#94A3B8; font-size:12px; font-weight:700;">📉 GASTOS (CAMPO / BOLAS)</div><div style="color:#EF4444; font-size:26px; font-weight:900; margin-top:5px;">{gastos_b2}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div style="background:#070D18; border:1px solid #1E293B; border-radius:10px; padding:15px; text-align:center;"><div style="color:#94A3B8; font-size:12px; font-weight:700;">💵 SALDO ATUAL EM CAIXA</div><div style="color:#38BDF8; font-size:26px; font-weight:900; margin-top:5px;">{saldo_caixa}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Bloco de Informações Pix do Clube
st.markdown("""
### 📱 PAGAMENTO DA MENSALIDADE VIA PIX
* **Valor:** <span style="color:#10B981; font-weight:800; font-size:18px;">R$ 20,00</span>
* **Vencimento:** **Até dia 11 de cada mês**
""", unsafe_allow_html=True)

st.markdown("""
<div class="pix-key-box">
    🔑 <b>Chave Pix (Telefone):</b><br>
    <b style="color:#10B981; font-size:18px;">43 999762318</b> — <i>Juel Ferreira</i>
</div>
""", unsafe_allow_html=True)

st.code("43999762318", language="text")

st.markdown("<br>", unsafe_allow_html=True)

col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    with st.expander("📋 Status das Mensalidades (Mês Atual)"):
        if lista_pagos or lista_pendentes:
            st.markdown("##### ✅ **Atletas com Mensalidade Paga:**")
            if lista_pagos:
                html_pagos = "".join([
                    f'<div class="paid-player-pill">✅ <b>{atleta["nome"]}</b> ({atleta["valor"]})</div>'
                    for atleta in lista_pagos
                ])
                st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 15px;">{html_pagos}</div>', unsafe_allow_html=True)
            else:
                st.info("Nenhum pagamento registrado.")

            st.markdown("##### ❌ **Atletas com Mensalidade Pendente:**")
            if lista_pendentes:
                html_pendentes = "".join([
                    f'<div class="unpaid-player-pill">❌ <b>{atleta["nome"]}</b></div>'
                    for atleta in lista_pendentes
                ])
                st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">{html_pendentes}</div>', unsafe_allow_html=True)
            else:
                st.success("Todos os atletas estão em dia!")
        else:
            st.info("Nenhum registro de mensalidade encontrado.")

with col_exp2:
    with st.expander("📉 Ver Detalhamento de Gastos"):
        if detalhe_gastos:
            df_g = pd.DataFrame(detalhe_gastos)
            df_g.columns = ["Descrição do Gasto", "Valor"]
            st.dataframe(df_g, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum gasto específico detalhado na Coluna H até o momento.")
