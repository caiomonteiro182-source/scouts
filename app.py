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
        min-height: 120px;
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
# 4. CARREGAMENTO DAS QUATRO PLANILHAS E CLIMA
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

@st.cache_data(ttl=0)
def load_financial_stats():
    try:
        df_fin = pd.read_csv(URL_FINANCEIRO)
        df_fin.columns = df_fin.columns.str.strip()
        return df_fin
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
# 6. CARDS SUPERIORES COM TEMPORIZADOR (APENAS DIAS, HORAS E MINUTOS)
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

agora = datetime.now()
dias_ate_sabado = (5 - agora.weekday()) % 7
if dias_ate_sabado == 0 and agora.hour >= 16:
    dias_ate_sabado = 7

proximo_jogo = (agora + timedelta(days=dias_ate_sabado)).replace(hour=16, minute=0, second=0, microsecond=0)
target_date_str = proximo_jogo.isoformat()

# Atualizado para omitir os segundos e manter apenas dias, horas e minutos
timer_html = f"""
<div style="display: flex; gap: 8px; margin-top: 10px; align-items: center; justify-content: center;">
    <span style="font-size: 11px; font-weight: 800; color: #38BDF8;">⏳ FALTAM:</span>
    <div style="background: #0B1329; border: 1px solid #1E3A8A; border-radius: 6px; padding: 3px 8px; text-align: center;">
        <span id="timer-days" style="font-size: 13px; font-weight: 900; color: #FFF;">--d</span>
    </div>
    <div style="background: #0B1329; border: 1px solid #1E3A8A; border-radius: 6px; padding: 3px 8px; text-align: center;">
        <span id="timer-hours" style="font-size: 13px; font-weight: 900; color: #FFF;">--h</span>
    </div>
    <div style="background: #0B1329; border: 1px solid #1E3A8A; border-radius: 6px; padding: 3px 8px; text-align: center;">
        <span id="timer-minutes" style="font-size: 13px; font-weight: 900; color: #FFF;">--m</span>
    </div>
</div>

<img src onerror='
    var countDownDate = new Date("{target_date_str}").getTime();
    function updateCountdown() {{
        var now = new Date().getTime();
        var distance = countDownDate - now;
        
        if (distance < 0) return;
        
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        
        var d = document.getElementById("timer-days");
        if(d) d.innerHTML = String(days).padStart(2, "0") + "d";
        var h = document.getElementById("timer-hours");
        if(h) h.innerHTML = String(hours).padStart(2, "0") + "h";
        var m = document.getElementById("timer-minutes");
        if(m) m.innerHTML = String(minutes).padStart(2, "0") + "m";
    }}
    updateCountdown();
    setInterval(updateCountdown, 1000);
' style="display:none;">
"""

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

        configs_colunas = {col: st.column_config.Column(alignment="center") for col in df_historico_jogos.columns}

        st.dataframe(
            df_historico_jogos,
            use_container_width=True,
            hide_index=True,
            column_config=configs_colunas
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

    # ==========================================
    # 9. SEÇÃO FINANCEIRA DO CLUBE (RODAPÉ)
    # ==========================================
    df_financeiro = load_financial_stats()

    entradas_val = 0.0
    saidas_val = 0.0
    saldo_caixa_val = 0.0

    try:
        if not df_financeiro.empty:
            for idx, row in df_financeiro.iterrows():
                row_str = str(row.values).lower()
                
                def extract_money(linha):
                    for val in linha:
                        if pd.isna(val): continue
                        v_str = str(val).lower().strip()
                        if any(w in v_str for w in ['entrada', 'saida', 'saída', 'saldo', 'caixa', 'receita', 'despesa']):
                            continue
                        
                        v_str = v_str.replace('r$', '').replace(' ', '')
                        if ',' in v_str:
                            v_str = v_str.replace('.', '').replace(',', '.')
                            
                        try:
                            return float(v_str)
                        except ValueError:
                            continue
                    return 0.0

                if "entrada" in row_str or "arrecada" in row_str or "receita" in row_str:
                    entradas_val += extract_money(row.values)
                elif "saída" in row_str or "saida" in row_str or "gasto" in row_str or "despesa" in row_str:
                    saidas_val += extract_money(row.values)
                elif "saldo" in row_str or "caixa" in row_str:
                    saldo_caixa_val = extract_money(row.values)

            if saldo_caixa_val == 0.0 and (entradas_val > 0 or saidas_val > 0):
                saldo_caixa_val = entradas_val - saidas_val

    except Exception:
        pass

    def format_brl(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    entradas = format_brl(entradas_val)
    saidas = format_brl(saidas_val)
    saldo_caixa = format_brl(saldo_caixa_val)

    card_financeiro_html = f"""
    <div class="financial-card">
        <div class="financial-title">💰 PAINEL FINANCEIRO DO CLUBE</div>
        <div class="fin-summary-box">
            <div class="fin-item">
                <div class="fin-label">📈 Entradas Totais (Mensalidades / Arrecadações)</div>
                <div class="fin-value-green">{entradas}</div>
            </div>
            <div class="fin-item">
                <div class="fin-label">📉 Saídas Totais (Campo / Bolas / Coletes)</div>
                <div class="fin-value-red">{saidas}</div>
            </div>
            <div class="fin-item">
                <div class="fin-label">💵 Saldo Atual em Caixa</div>
                <div class="fin-value-blue">{saldo_caixa}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(textwrap.dedent(card_financeiro_html), unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar dados das planilhas: {e}")
