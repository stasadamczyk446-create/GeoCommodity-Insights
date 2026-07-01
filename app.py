# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
import os
import base64
import plotly.express as px
import pandas as pd
import numpy as np
import re

# --- 1. Konfiguracja Strony ---
st.set_page_config(page_title="GeoCommodity Insights", layout="wide", page_icon="🌍")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, .brand-title {
        font-family: 'Poppins', sans-serif !important;
    }

    /* --- Tło aplikacji --- */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #1b2440 0%, transparent 45%),
                    radial-gradient(circle at 85% 85%, #241b40 0%, transparent 45%),
                    linear-gradient(160deg, #0b0f1e 0%, #10152b 50%, #0b0f1e 100%);
        background-attachment: fixed;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1226 0%, #131a33 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #c7cde3 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08);
    }

    /* --- Sidebar header --- */
    .sidebar-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.05em;
        color: #f0f2ff;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sidebar-sub {
        color: #7b83a8 !important;
        font-size: 0.78em;
        margin-bottom: 14px;
    }

    /* --- Inputy / selecty --- */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    .stTextInput input {
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #f0f2ff !important;
    }
    div[data-baseweb="select"]:hover > div {
        border-color: rgba(120,140,255,0.5) !important;
    }
    .stTextInput input {
        color: #f0f2ff !important;
    }

    /* --- Radio jako "pill tabs" --- */
    div[role="radiogroup"] {
        background: rgba(255,255,255,0.04);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        gap: 4px !important;
    }
    div[role="radiogroup"] label {
        background: transparent;
        border-radius: 8px;
        padding: 6px 10px !important;
        transition: all 0.2s ease;
    }

    /* --- Hero header --- */
    .hero-wrap {
        text-align: center;
        padding: 10px 0 6px 0;
    }
    .brand-title {
        font-size: 2.6em;
        font-weight: 800;
        background: linear-gradient(90deg, #7dd3fc 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .brand-slogan {
        color: #8b93b8;
        font-size: 1.0em;
        font-weight: 500;
        margin-top: -8px;
    }

    /* --- Status pill --- */
    .status-container {
        text-align: center;
        margin-top: 14px;
        margin-bottom: 22px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 20px;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 0.9em;
        font-weight: 500;
        color: #a7afd1;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4ade80;
        box-shadow: 0 0 8px #4ade80;
    }
    .status-dot.working {
        background: #fbbf24;
        box-shadow: 0 0 8px #fbbf24;
        animation: pulse 1.2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
    .status-highlight {
        color: #e4e7f7;
        font-weight: 700;
    }

    /* --- Karta wyboru (glass card) --- */
    .glass-card {
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 22px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    .glass-card-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.05em;
        color: #e4e7f7;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .glass-card-sub {
        color: #7b83a8;
        font-size: 0.85em;
        margin-bottom: 18px;
    }

    /* --- Report card --- */
    .report-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        padding: 36px 38px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.09);
        margin-top: 22px;
        color: #dde1f5;
        line-height: 1.75;
        animation: fadeIn 0.6s ease;
    }
    .report-card h3 {
        color: #f0f2ff;
        border-bottom: 1px solid rgba(255,255,255,0.12);
        padding-bottom: 14px;
        margin-bottom: 18px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .report-card b {
        color: #a5b4fc;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- Przycisk generuj --- */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 0 !important;
        font-weight: 700 !important;
        font-family: 'Poppins', sans-serif !important;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 20px rgba(139,92,246,0.35);
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 28px rgba(139,92,246,0.55);
        transform: translateY(-2px);
    }

    /* --- Progress bar --- */
    .stProgress > div > div > div > div {
        background: var(--p-color);
        border-radius: 999px;
    }
    .stProgress > div > div > div {
        background-color: rgba(255,255,255,0.08) !important;
        border-radius: 999px;
    }

    /* --- Score badge --- */
    .score-badge-wrap {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 20px 24px;
        margin-top: 22px;
        backdrop-filter: blur(20px);
    }
    .score-title {
        color: #a7afd1;
        font-size: 0.85em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    .score-status-text {
        font-weight: 700;
        margin-top: 10px;
        font-size: 0.95em;
    }

    /* --- Metric cards row --- */
    .metric-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 18px 20px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(139,92,246,0.4);
    }
    .metric-icon {
        font-size: 1.6em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.3em;
        color: #f0f2ff;
    }
    .metric-label {
        color: #7b83a8;
        font-size: 0.78em;
        margin-top: 2px;
    }

    /* --- Footer --- */
    .footer-text {
        text-align: center;
        font-size: 0.82em;
        color: #5a6188;
        padding: 20px 0 10px 0;
    }
    .footer-text b {
        color: #7b83a8;
    }

    /* --- Chart container --- */
    .chart-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 6px;
    }

    /* --- Divider ładniejszy --- */
    hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 22px 0 !important;
    }

    /* --- Error / spinner text --- */
    .stSpinner > div {
        color: #a7afd1 !important;
    }

    /* --- selectbox label --- */
    .stSelectbox label, .stRadio label, .stTextInput label {
        color: #c7cde3 !important;
        font-weight: 500 !important;
        font-size: 0.92em !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Baza Danych Rezerw Złota ---
gold_data = {
    'Country': ['USA', 'Niemcy', 'Włochy', 'Francja', 'Rosja', 'Chiny', 'Szwajcaria', 'Japonia', 'Indie', 'Turcja', 'Holandia', 'Polska', 'Arabia Saudyjska', 'Portugalia', 'Kazachstan', 'Uzbekistan', 'Hiszpania', 'Austria', 'Tajlandia', 'Belgia', 'Algieria', 'Wenezuela', 'Filipiny', 'Brazylia', 'Singapur', 'Szwecja', 'RPA', 'Meksyk', 'Libia', 'Grecja', 'Korea Południowa', 'Rumunia', 'Egipt', 'Australia', 'Kuwejt', 'Indonezja', 'Katar', 'Pakistan', 'Argentyna', 'ZEA', 'Malezja', 'Ukraina', 'Jordania', 'Słowacja', 'Węgry', 'Bułgaria', 'Białoruś', 'Finlandia', 'Serbia', 'Peru'],
    'ISO_Code': ['USA', 'DEU', 'ITA', 'FRA', 'RUS', 'CHN', 'CHE', 'JPN', 'IND', 'TUR', 'NLD', 'POL', 'SAU', 'PRT', 'KAZ', 'UZB', 'ESP', 'AUT', 'THA', 'BEL', 'DZA', 'VEN', 'PHL', 'BRA', 'SGP', 'SWE', 'ZAF', 'MEX', 'LBY', 'GRC', 'KOR', 'ROU', 'EGY', 'AUS', 'KWT', 'IDN', 'QAT', 'PAK', 'ARG', 'ARE', 'MYS', 'UKR', 'JOR', 'SVK', 'HUN', 'BGR', 'BLR', 'FIN', 'SRB', 'PER'],
    'Tons': [8133, 3352, 2451, 2436, 2332, 2264, 1040, 846, 822, 584, 612, 359, 323, 382, 309, 362, 281, 280, 244, 227, 173, 161, 155, 129, 230, 126, 125, 120, 116, 114, 104, 103, 126, 79, 79, 78, 106, 64, 61, 74, 45, 27, 43, 31, 94, 40, 53, 49, 38, 34]
}
df_gold = pd.DataFrame(gold_data)
df_gold['Log_Tons'] = np.log10(df_gold['Tons'])

# --- 3. Baza Danych Zagrożeń Globalnych ---
threat_data = {
    'Country': [
        'Ukraina', 'Rosja', 'Izrael', 'Palestyna', 'Syria', 'Jemen', 'Tajwan', 'Korea Północna', 'Iran', 
        'Afganistan', 'Somalia', 'Mali', 'Burkina Faso', 'Niger', 'DR Konga', 'Wenezuela', 'Argentyna', 
        'Turcja', 'Egipt', 'Pakistan', 'Liban', 'Meksyk', 'Mjanma', 'Irak', 'Gruzja', 'Nigeria', 'Kuba'
    ],
    'ISO_Code': [
        'UKR', 'RUS', 'ISR', 'PSE', 'SYR', 'YEM', 'TWN', 'PRK', 'IRN', 
        'AFG', 'SOM', 'MLI', 'BFA', 'NER', 'COD', 'VEN', 'ARG', 
        'TUR', 'EGY', 'PAK', 'LBN', 'MEX', 'MMR', 'IRQ', 'GEO', 'NGA', 'CUB'
    ],
    'Kategoria': [
        'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Niestabilność Polityczna', 'Niestabilność Polityczna', 'Niestabilność Polityczna', 
        'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 
        'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Konflikt zbrojny', 'Konflikt zbrojny', 
        'Niestabilność Polityczna', 'Niestabilność Polityczna', 'Terroryzm', 'Kryzys Gospodarczy'
    ]
}
df_threats = pd.DataFrame(threat_data)

color_map_threats = {
    'Wojna': '#ef4444',
    'Konflikt zbrojny': '#dc2626',
    'Niestabilność Polityczna': '#f97316',
    'Terroryzm': '#ea580c',
    'Kryzys Gospodarczy': '#a855f7'
}

ALL_COUNTRIES = sorted([
    "Afganistan", "Albania", "Algieria", "Andora", "Angola", "Arabia Saudyjska", "Argentyna", "Armenia", "Australia", "Austria",
    "Azerbejdżan", "Bahamy", "Bahrajn", "Bangladesz", "Barbados", "Belgia", "Belize", "Benin", "Bhutan", "Białoruś", "Boliwia",
    "Bośnia i Hercegowina", "Botswana", "Brazylia", "Brunei", "Bułgaria", "Burkina Faso", "Burundi", "Chile", "Chiny", "Chorwacja",
    "Cypr", "Czad", "Czarnogóra", "Czechy", "Dania", "Egipt", "Ekwador", "Erytrea", "Estonia", "Etiopia", "Filipiny", "Finlandia", 
    "Francja", "Gabon", "Gambia", "Ghana", "Grecja", "Gruzja", "Gwatemala", "Gwinea", "Haiti", "Hiszpania", "Holandia", "Honduras", 
    "Indie", "Indonezja", "Irak", "Iran", "Irlandia", "Islandia", "Izrael", "Jamajka", "Japonia", "Jemen", "Jordania", "Kambodża", 
    "Kamerun", "Kanada", "Katar", "Kazachstan", "Kenia", "Kirgistan", "Kolumbia", "Kongo", "Korea Południowa", "Korea Północna", 
    "Kostaryka", "Kuba", "Kuwejt", "Laos", "Liban", "Liberia", "Libia", "Litwa", "Luksemburg", "Łotwa", "Macedonia Północna", 
    "Madagaskar", "Malezja", "Malta", "Maroko", "Meksyk", "Mołdawia", "Monako", "Mongolia", "Mozambik", "Namibia", "Nepal", 
    "Niemcy", "Niger", "Nigeria", "Nikaragua", "Norwegia", "Nowa Zelandia", "Oman", "Pakistan", "Panama", "Paragwaj", "Peru", 
    "Polska", "Portugalia", "Republika Południowej Afryki", "Rosja", "Rumunia", "Rwanda", "Salwador", "Senegal", "Serbia", 
    "Singapur", "Słowacja", "Słowenia", "Somalia", "Sri Lanka", "Sudan", "Surinam", "Syria", "Szwajcaria", "Szwecja", "Tadżykistan", 
    "Tajlandia", "Tajwan", "Tanzania", "Tunezja", "Turcja", "Turkmenistan", "Uganda", "Ukraina", "Urugwaj", "USA", "Uzbekistan", 
    "Wenezuela", "Węgry", "Wielka Brytania", "Wietnam", "Włochy", "Wybrzeże Kości Słoniowej", "Zambia", "Zimbabwe", "ZEA"
])

COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór", "Miedź", "Aluminium", "Żelazo", "Nikiel", "Cynk", "Złoto", "Srebro", "Platyna", "Lit", "Kobalt", "Metale Ziem Rzadkich", "Grafit", "Krzem", "Magnez", "Pszenica (Zboże)", "Kukurydza", "Rzepak", "Ryż", "Kawa", "Kauczuk"])

# --- 4. Języki ---
LANG = {
    "Polska 🇵🇱": {
        "code": "PL", "slogan": "Strategiczna Analityka wspierana przez AI",
        "api_label": "Klucz API OpenAI", "nav_analysis": "Analiza Tekstowa",
        "nav_maps": "Moduł Wizualny", "mode_label": "Wybierz tryb:",
        "mode_res": "Surowce Strategiczne", "mode_pol": "Polityka", "mode_rel": "Analiza Relacji",
        "map_option_off": "Wyłączony", "map_option_gold": "Mapa Rezerw Złota", "map_option_threats": "Globalny Monitor Zagrożeń",
        "country_label": "Wybierz Państwo:", "country2_label": "Wybierz drugie Państwo:",
        "res_label": "Wybierz Surowiec:", "pol_submode_label": "Obszar polityki:",
        "pol_options": ["Partie Polityczne", "System Władzy", "Główne Osoby w Państwie"],
        "btn_gen": "🚀 GENERUJ RAPORT", "status_wait": "Oczekiwanie na instrukcje",
        "status_work": "Generowanie raportu...", "loading": "Trwa analiza...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski",
        "score_label": "Wskaźnik Bezpieczeństwa Strategicznego (1-10):",
        "config_title": "Konfiguracja", "config_sub": "Ustaw parametry analizy",
        "select_title": "Parametry Analizy", "select_sub": "Wybierz państwo oraz przedmiot analizy",
        "m1_label": "Państwa w bazie", "m2_label": "Surowce", "m3_label": "Zagrożenia globalne", "m4_label": "Model AI"
    },
    "English 🇬🇧": {
        "code": "EN", "slogan": "AI-Powered Strategic Intelligence",
        "api_label": "OpenAI API Key", "nav_analysis": "Textual Analysis",
        "nav_maps": "Visual Module", "mode_label": "Select mode:",
        "mode_res": "Strategic Commodities", "mode_pol": "Politics", "mode_rel": "Relationship Analysis",
        "map_option_off": "Disabled", "map_option_gold": "Gold Reserves Map", "map_option_threats": "Global Threat Monitor",
        "country_label": "Select Country:", "country2_label": "Select second Country:",
        "res_label": "Select Commodity:", "pol_submode_label": "Politics area:",
        "pol_options": ["Political Parties", "Government System", "Key Figures"],
        "btn_gen": "🚀 GENERATE REPORT", "status_wait": "Ready & Waiting",
        "status_work": "Generating report...", "loading": "Analyzing...",
        "footer": "Educational Project - University of Warsaw",
        "score_label": "Strategic Security Score (1-10):",
        "config_title": "Configuration", "config_sub": "Set analysis parameters",
        "select_title": "Analysis Parameters", "select_sub": "Choose country and analysis target",
        "m1_label": "Countries in DB", "m2_label": "Commodities", "m3_label": "Global threats", "m4_label": "AI Model"
    }
}

# --- 5. Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">🌍 GeoCommodity</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Insights Terminal v2.0</div>', unsafe_allow_html=True)

    lang_display = st.selectbox("🌐 Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")

    st.markdown(f'<div class="sidebar-title" style="font-size:0.95em;">📂 {L["nav_analysis"]}</div>', unsafe_allow_html=True)
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"], L["mode_rel"]], label_visibility="collapsed")
    st.markdown("---")

    st.markdown(f'<div class="sidebar-title" style="font-size:0.95em;">🗺️ {L["nav_maps"]}</div>', unsafe_allow_html=True)
    map_selection = st.selectbox(" ", [L["map_option_off"], L["map_option_gold"], L["map_option_threats"]], label_visibility="collapsed")
    st.markdown("---")

    st.markdown(f'<div class="sidebar-title" style="font-size:0.95em;">⚙️ {L["config_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-sub">{L["config_sub"]}</div>', unsafe_allow_html=True)
    model_version = st.selectbox("🤖 Model AI:", ["gpt-4o-mini", "gpt-4o"])
    api_key = st.text_input(f"🔑 {L['api_label']}", type="password")

# --- 6. Logo / Hero Header ---
def get_transparent_logo_base64(file_path):
    """Wczytuje logo i usuwa białe/jasne tło, zwracając obraz PNG (RGBA) jako base64."""
    from PIL import Image
    import numpy as np
    from io import BytesIO

    img = Image.open(file_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Piksele czysto białe -> w pełni przezroczyste
    white_mask = (r > 235) & (g > 235) & (b > 235)
    data[:, :, 3] = np.where(white_mask, 0, 255)

    # Piksele prawie białe (antyaliasing na krawędziach liter) -> częściowa przezroczystość
    near_white = (r > 200) & (g > 200) & (b > 200) & ~white_mask
    avg = (r.astype(int) + g.astype(int) + b.astype(int)) / 3
    alpha_partial = np.clip((255 - avg) / (255 - 200) * 255, 0, 255).astype(np.uint8)
    data[:, :, 3] = np.where(near_white, alpha_partial, data[:, :, 3])

    result = Image.fromarray(data, "RGBA")
    buffer = BytesIO()
    result.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

if os.path.exists("logo.png"):
    encoded_logo = get_transparent_logo_base64("logo.png")
    st.markdown(f'''
        <div style="display: flex; justify-content: center; align-items: center; padding-top: 15px; background: transparent;">
            <img src="data:image/png;base64,{encoded_logo}" width="420" style="background: transparent; filter: drop-shadow(0 4px 20px rgba(139,92,246,0.25));">
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="brand-title">🌍 GeoCommodity Insights</div>
        <div class="brand-slogan">{L['slogan']}</div>
    </div>
    """, unsafe_allow_html=True)

status_placeholder = st.empty()
status_placeholder.markdown(f'''
    <div class="status-container">
        <div class="status-pill">
            <span class="status-dot"></span>
            {L["slogan"]} · <span class="status-highlight">{L["status_wait"]}</span>
        </div>
    </div>
''', unsafe_allow_html=True)

# --- 6b. Metric cards ---
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
with mcol1:
    st.markdown(f'''<div class="metric-card"><div class="metric-icon">🌐</div>
        <div class="metric-value">{len(ALL_COUNTRIES)}</div>
        <div class="metric-label">{L["m1_label"]}</div></div>''', unsafe_allow_html=True)
with mcol2:
    st.markdown(f'''<div class="metric-card"><div class="metric-icon">💎</div>
        <div class="metric-value">{len(COMMODITIES)}</div>
        <div class="metric-label">{L["m2_label"]}</div></div>''', unsafe_allow_html=True)
with mcol3:
    st.markdown(f'''<div class="metric-card"><div class="metric-icon">⚠️</div>
        <div class="metric-value">{len(df_threats)}</div>
        <div class="metric-label">{L["m3_label"]}</div></div>''', unsafe_allow_html=True)
with mcol4:
    st.markdown(f'''<div class="metric-card"><div class="metric-icon">🤖</div>
        <div class="metric-value" style="font-size:0.95em;">{model_version}</div>
        <div class="metric-label">{L["m4_label"]}</div></div>''', unsafe_allow_html=True)

st.markdown("---")

# --- 7. Interfejs Główny ---
if map_selection == L["map_option_gold"]:
    st.markdown(f'<div class="chart-header"><h3 style="color:#f0f2ff;">🥇 {L["map_option_gold"]}</h3></div>', unsafe_allow_html=True)
    fig = px.choropleth(df_gold, locations="ISO_Code", color="Log_Tons", hover_name="Country",
                        hover_data={"Log_Tons": False, "Tons": True},
                        color_continuous_scale="Spectral_r", labels={'Log_Tons':'Skala Potęgi', 'Tons': 'Tony'})
    fig.update_layout(
        geo=dict(showframe=False, projection_type='natural earth', bgcolor='rgba(0,0,0,0)',
                 landcolor='rgba(255,255,255,0.03)', showland=True,
                 subunitcolor='rgba(255,255,255,0.1)'),
        margin={"r":0,"t":20,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#c7cde3'
    )
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif map_selection == L["map_option_threats"]:
    st.markdown(f'<div class="chart-header"><h3 style="color:#f0f2ff;">🚨 {L["map_option_threats"]}</h3></div>', unsafe_allow_html=True)
    fig_threats = px.choropleth(df_threats, locations="ISO_Code", color="Kategoria", hover_name="Country",
                        color_discrete_map=color_map_threats, 
                        category_orders={"Kategoria": ["Wojna", "Konflikt zbrojny", "Niestabilność Polityczna", "Terroryzm", "Kryzys Gospodarczy"]},
                        labels={'Kategoria':''})
    fig_threats.update_layout(
        geo=dict(showframe=False, projection_type='natural earth', bgcolor='rgba(0,0,0,0)',
                 landcolor='rgba(255,255,255,0.03)', showland=True,
                 subunitcolor='rgba(255,255,255,0.1)'),
        margin={"r":0,"t":20,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#c7cde3',
        legend=dict(bgcolor='rgba(255,255,255,0.05)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1)
    )
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.plotly_chart(fig_threats, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f'''
        <div class="glass-card-title">🎯 {L["select_title"]}</div>
        <div class="glass-card-sub">{L["select_sub"]}</div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: selected_country = st.selectbox(f"📍 {L['country_label']}", ALL_COUNTRIES)
    with col2:
        if analysis_mode == L["mode_res"]: target_item = st.selectbox(f"💎 {L['res_label']}", COMMODITIES)
        elif analysis_mode == L["mode_pol"]: target_item = st.selectbox(f"🔍 {L['pol_submode_label']}", L["pol_options"])
        else: target_item = st.selectbox(f"🤝 {L['country2_label']}", ALL_COUNTRIES, index=1)

    st.write("")
    generate_clicked = st.button(L["btn_gen"], use_container_width=True)

    if generate_clicked:
        if not api_key: 
            st.error("⚠️ Podaj klucz API!")
        else:
            try:
                status_placeholder.markdown(f'''
                    <div class="status-container">
                        <div class="status-pill">
                            <span class="status-dot working"></span>
                            {L["slogan"]} · <span class="status-highlight" style="color: #fbbf24;">{L["status_work"]}</span>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                client = OpenAI(api_key=api_key)
                with st.spinner(L["loading"]):
                    prompt = f"Analiza {target_item} w {selected_country}. {analysis_mode}. Nie używaj żadnych hasztagów (#). Nagłówki sekcji zapisuj jako pogrubiony tekst zakończony dwukropkiem (np. **Tytuł sekcji:**). Na samym końcu napisz tylko: SCORE: X (gdzie X to liczba 1-10)."
                    resp = client.chat.completions.create(model=model_version,
                        messages=[{"role": "system", "content": f"Ekspert geopolityki. Język: {L['code']}."},
                                  {"role": "user", "content": prompt}])
                    full_response = resp.choices[0].message.content
                    processed_text = re.sub(r'^#+\s*(.*)', r'**\1:**', full_response, flags=re.MULTILINE)
                    score_match = re.search(r"SCORE:\s*(\d+)", processed_text)
                    clean_report = re.sub(r"SCORE:\s*\d+", "", processed_text)
                    
                    if score_match:
                        score_val = int(score_match.group(1))
                        if score_val >= 9: color_hex = "#4ade80"; status_txt = "Optymalny"; status_icon = "✅"
                        elif score_val >= 7: color_hex = "#60a5fa"; status_txt = "Stabilny"; status_icon = "🔵"
                        elif score_val >= 4: color_hex = "#fbbf24"; status_txt = "Umiarkowane ryzyko"; status_icon = "🟡"
                        else: color_hex = "#f87171"; status_txt = "Wysokie ryzyko"; status_icon = "🔴"

                        st.markdown(f'<style>div[data-testid="stProgress"] > div > div > div > div {{ background: {color_hex} !important; box-shadow: 0 0 12px {color_hex}80; }}</style>', unsafe_allow_html=True)
                        st.markdown('<div class="score-badge-wrap">', unsafe_allow_html=True)
                        st.markdown(f'<div class="score-title">{L["score_label"]}</div>', unsafe_allow_html=True)
                        st.progress(score_val / 10)
                        st.markdown(f'<p class="score-status-text" style="color:{color_hex};">{status_icon} {status_txt} — {score_val}/10</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown(f'<div class="report-card"><h3>📄 {selected_country} · {target_item}</h3>{clean_report.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                status_placeholder.markdown(f'''
                    <div class="status-container">
                        <div class="status-pill">
                            <span class="status-dot"></span>
                            {L["slogan"]} · <span class="status-highlight">{L["status_wait"]}</span>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            except Exception as e: 
                st.error(f"❌ Błąd: {e}")

st.markdown("---")
st.markdown(f"<div class='footer-text'>© 2026 <b>GeoCommodity Insights</b> · {L['footer']}</div>", unsafe_allow_html=True)
