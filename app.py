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

        .info-card {
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

    /* Contagem Regressiva do Jogo */
    .timer-container {
        background-color: #0B1329;
        border: 1px solid #1E3A8A;
        border-radius: 8px;
        padding: 6px 12px;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: #38BDF8;
        font-weight: 800;
        font-size: 13px;
        width: fit-content;
    }

    .timer-digits {
        color: #FFFFFF;
        font-family: monospace;
        font-size: 14px;
        letter-spacing: 1px;
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

    /* Card Financeiro Rodapé */
    .financial-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-top: 4px solid #10B981;
        border-radius: 15px;
        padding: 25px;
        margin-top: 40px;
        margin-bottom: 30px;
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
# 4. CARREGAMENTO DAS TRÊS PLANILHAS E CLIMA
# ==========================================
ID_PLANILHA_STATS = "1E0wlg8BvOVdp_dk-dn1zw7HAhBh-cjhD269YBu-SkOQ"
URL_STATS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_STATS}/export?format=csv"

ID_PLANILHA_VITORIAS = "1e9VpoNzzqYZlD8JFJxWLQiWhNw4AaKiycauCZDxAas0"
GID_VITORIAS = "1092123094"
URL_VITORIAS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_VITORIAS}/export?format=csv&gid={GID_VITORIAS}"

ID_PLANILHA_JOGOS = "1Chjvd4vBarn9O4EgXWFnyMe5uIBgUsa4QCHIRr8C6Tk"
GID_JOGOS = "1092123094"
URL_JOGOS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA_JOGOS}/export?format=csv&gid={GID_JOGOS}"

@st.cache_data(ttl=0)
def load_player_stats():
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
    try:
        df_vic = pd.read_csv(URL_VITORIAS)
        df_vic.columns = df_vic.columns.str.strip()
        return df_vic
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

def get_next_saturday_target():
    today = datetime.now()
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0 and today.hour >= 18:
        days_until_saturday = 7
    next_saturday = today + timedelta(days=days_until_saturday)
    return next_saturday.replace(hour=16, minute=0, second=0, microsecond=0)

@st.cache_data(ttl=3600)
def get_next_saturday_weather():
    try:
        next_saturday = get_next_saturday_target()
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
# 6. CARDS SUPERIORES E TEMPORIZADOR
# ==========================================
df_players = load_player_stats()
df_vitorias = load_victories_stats()

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

target_sat = get_next_saturday_target()
iso_target = target_sat.isoformat()
data_jogo = weather_info.get('data', '')
data_str = f" ({data_jogo})" if data_jogo else ""

col_jogo, col_placar = st.columns(2)

with col_jogo:
    card_jogo_html = f"""
    <div class="info-card card-border-blue">
        <div class="card-tag">📍 PRÓXIMO ENCONTRO</div>
        <div class="card-main-text">Sábado{data_str} às 16:00 • Cambé - PR</div>
        <div>{weather_html}</div>
        <div class="timer-container">
            <span>⏳ FALTAM:</span>
            <span id="fcb-timer" class="timer-digits">Calculando...</span>
        </div>
    </div>
    <script>
        (function() {{
            const targetDate = new Date("{iso_target}").getTime();
            function updateTimer() {{
                const now = new Date().getTime();
                const distance = targetDate - now;
                const timerElem = document.getElementById("fcb-timer");
                if (!timerElem) return;

                if (distance < 0) {{
                    timerElem.innerHTML = "⚽ JOGO EM ANDAMENTO / REALIZADO!";
                    return;
                }}

                const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((distance % (1000 * 60)) / 1Para criar um temporizador dinâmico e em tempo real no Streamlit sem travar a aplicação, a melhor prática é usar um componente HTML com JavaScript nativo embutido via `st.components.v1.html`. Dessa forma, o relógio faz a contagem regressiva segundo a segundo diretamente no navegador do usuário, calculando automaticamente quanto tempo falta até o próximo sábado às 16:00.

Substitua a **Seção 6 (CARDS SUPERIORES)** do seu `app.py` pelo bloco abaixo:

```python
# Importe o módulo de componentes no topo do arquivo junto aos outros imports:
import streamlit.components.v1 as components

# ==========================================
# 6. CARDS SUPERIORES (COM TEMPORIZADOR)
# ==========================================
df_players = load_player_stats()
df_vitorias = load_victories_stats()

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
    weather_text = f"{weather_info['condicao']} • 🌡️ {weather_info['temp']} • 🌧️ Chuva: {weather_info['pop']}"
else:
    weather_text = "⚽ Dia de Jogo Confirmado"

data_jogo = weather_info.get('data', '')
data_str = f" ({data_jogo})" if data_jogo else ""

col_jogo, col_placar = st.columns(2)

with col_jogo:
    # Componente HTML/JS para contagem regressiva em tempo real até sábado às 16:00
    countdown_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="[https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&display=swap](https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&display=swap)" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: transparent;
                font-family: 'Montserrat', sans-serif;
                color: #F1F5F9;
            }}
            .info-card {{
                background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
                border: 1px solid #334155;
                border-left: 5px solid #38BDF8;
                border-radius: 12px;
                padding: 16px 20px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                box-sizing: border-box;
            }}
            .card-tag {{
                color: #38BDF8;
                font-size: 11px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .card-main-text {{
                color: #FFFFFF;
                font-size: 15px;
                font-weight: 700;
                margin-top: 4px;
            }}
            .timer-box {{
                display: flex;
                gap: 8px;
                margin-top: 10px;
                align-items: center;
            }}
            .timer-unit {{
                background: #0B1329;
                border: 1px solid #1E3A8A;
                border-radius: 8px;
                padding: 4px 10px;
                text-align: center;
                min-width: 45px;
            }}
            .timer-num {{
                font-size: 16px;
                font-weight: 900;
                color: #38BDF8;
            }}
            .timer-lbl {{
                font-size: 9px;
                font-weight: 700;
                color: #94A3B8;
                text-transform: uppercase;
            }}
            .weather-pill {{
                background-color: #0F2144;
                border: 1px solid #1E3A8A;
                border-radius: 20px;
                padding: 4px 12px;
                color: #F1F5F9;
                font-size: 12px;
                font-weight: 700;
                display: inline-block;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="info-card">
            <div class="card-tag">📍 PRÓXIMO ENCONTRO</div>
            <div class="card-main-text">Sábado{data_str} às 16:00 • Cambé - PR</div>
            
            <div class="timer-box">
                <div class="timer-unit"><div class="timer-num" id="dias">00</div><div class="timer-lbl">Dias</div></div>
                <div class="timer-unit"><div class="timer-num" id="horas">00</div><div class="timer-lbl">Horas</div></div>
                <div class="timer-unit"><div class="timer-num" id="min">00</div><div class="timer-lbl">Min</div></div>
                <div class="timer-unit"><div class="timer-num" id="seg">00</div><div class="timer-lbl">Seg</div></div>
            </div>

            <div class="weather-pill">{weather_text}</div>
        </div>

        <script>
            function getNextSaturday16() {{
                const now = new Date();
                const target = new Date();
                
                let daysUntilSaturday = (5 - now.getDay() + 7) % 7;
                
                // Se hoje for sábado e já passou das 16:00, aponta para o próximo sábado
                if (daysUntilSaturday === 0 && now.getHours() >= 16) {{
                    daysUntilSaturday = 7;
                }}
                
                target.setDate(now.getDate() + daysUntilSaturday);
                target.setHours(16, 0, 0, 0);
                return target.getTime();
            }}

            const targetTime = getNextSaturday16();

            function updateTimer() {{
                const now = new Date().getTime();
                const diff = targetTime - now;

                if (diff <= 0) {{
                    document.getElementById("dias").innerText = "00";
                    document.getElementById("horas").innerText = "00";
                    document.getElementById("min").innerText = "00";
                    document.getElementById("seg").innerText = "00";
                    return;
                }}

                const d = Math.floor(diff / (1000 * 60 * 60 * 24));
                const h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const s = Math.floor((diff % (1000 * 60)) / 1000);

                document.getElementById("dias").innerText = d < 10 ? "0" + d : d;
                document.getElementById("horas").innerText = h < 10 ? "0" + h : h;
                document.getElementById("min").innerText = m < 10 ? "0" + m : m;
                document.getElementById("seg").innerText = s < 10 ? "0" + s : s;
            }}

            setInterval(updateTimer, 1000);
            updateTimer();
        </script>
    </body>
    </html>
    """
    components.html(countdown_html, height=170)

with col_placar:
    card_placar_html = (
        f'<div class="info-card card-border-gold" style="height: 170px;">'
        f'<div class="card-tag-gold">🏆 PLACAR GERAL DE VITÓRIAS</div>'
        f'<div class="scoreboard-box" style="margin-top: 20px;">'
        f'<span class="team-score score-red">🔴 Vermelho: {vitorias_vermelho}</span>'
        f'<span class="score-divider">X</span>'
        f'<span class="team-score score-blue">🔵 Azul: {vitorias_azul}</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_placar_html, unsafe_allow_html=True)
