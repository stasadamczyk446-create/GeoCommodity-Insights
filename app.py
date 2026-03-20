import streamlit as st
from openai import OpenAI
import os
import base64
import plotly.express as px
import pandas as pd

# --- 1. Konfiguracja Strony ---
st.set_page_config(page_title="GeoCommodity Insights", layout="wide", page_icon="🌍")

st.markdown("""
    <style>
    .report-card {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #eee;
        margin-top: 20px;
        color: #1e1e1e;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        color: #002d62;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Baza Danych (Podstawowe Statystyki) ---
# Rozszerzona lista o przykładowe dane - AI uzupełni resztę dynamicznie
COUNTRY_STATS = {
    "Polska": {"gdp": "$680B", "pop": "38M"},
    "USA": {"gdp": "$25.5T", "pop": "333M"},
    "Chiny": {"gdp": "$17.9T", "pop": "1.4B"},
    "Niemcy": {"gdp": "$4.1T", "pop": "83M"},
    "Indie": {"gdp": "$3.4T", "pop": "1.4B"},
    "Brazylia": {"gdp": "$1.9T", "pop": "214M"},
    "Arabia Saudyjska": {"gdp": "$1.1T", "pop": "36M"},
    "Australia": {"gdp": "$1.7T", "pop": "26M"},
    "Norwegia": {"gdp": "$579B", "pop": "5.4M"},
    "RPA": {"gdp": "$405B", "pop": "60M"}
}

ALL_COUNTRIES = sorted([
    "Afganistan", "Albania", "Algieria", "Arabia Saudyjska", "Argentyna", "Australia", "Austria", "Belgia", "Brazylia", 
    "Chile", "Chiny", "Czechy", "Dania", "Egipt", "Francja", "Grecja", "Hiszpania", "Indie", "Indonezja", "Irak", 
    "Iran", "Japonia", "Kanada", "Katar", "Kazachstan", "Kolumbia", "Korea Południowa", "Meksyk", "Niemcy", "Nigeria", 
    "Norwegia", "Pakistan", "Polska", "Portugalia", "Rosja", "RPA", "Szwajcaria", "Szwecja", "Turcja", "Ukraina", "USA", 
    "Uzbekistan", "Wenezuela", "Wielka Brytania", "Włochy", "ZEA"
])

COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór", "Miedź", "Aluminium", "Lit", "Kobalt", "Złoto", "Srebro", "Nikiel"])

# --- 3. Słownik Języków ---
LANG = {
    "Polska 🇵🇱": {
        "code": "PL",
        "slogan": "Strategiczna Analityka wspierana przez AI",
        "nav_analysis": "📂 ANALIZA TEKSTOWA",
        "nav_maps": "🗺️ MODUŁ WIZUALNY",
        "mode_res": "Surowce Strategiczne",
        "mode_pol": "Polityka",
        "mode_rel": "Analiza Relacji",
        "stat_gdp": "PKB (Nominalne)",
        "stat_pop": "Populacja",
        "map_option_gold": "Mapa Rezerw Złota",
        "btn_gen": "🚀 GENERUJ RAPORT",
        "loading": "Analizowanie danych...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski"
    },
    "English 🇬🇧": {
        "code": "EN",
        "slogan": "AI-Powered Strategic Intelligence",
        "nav_analysis": "📂 TEXTUAL ANALYSIS",
        "nav_maps": "🗺️ VISUAL MODULE",
        "mode_res": "Strategic Commodities",
        "mode_pol": "Politics",
        "mode_rel": "Relationship Analysis",
        "stat_gdp": "GDP (Nominal)",
        "stat_pop": "Population",
        "map_option_gold": "Gold Reserves Map",
        "btn_gen": "🚀 GENERATE REPORT",
        "loading": "Analyzing data...",
        "footer": "Educational Project - University of Warsaw"
    }
}

# --- 4. Sidebar ---
with st.sidebar:
    lang_display = st.selectbox("Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown(f"### {L['nav_analysis']}")
    analysis_mode = st.radio("Tryb:", [L["mode_res"], L["mode_pol"], L["mode_rel"]])
    st.markdown("---")
    st.markdown(f"### {L['nav_maps']}")
    map_selection = st.selectbox("Wybór mapy:", ["Wyłączona", L["map_option_gold"]])
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])

# --- 5. Logo ---
if os.path.exists("logo.png"):
    def get_base64_logo(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    st.markdown(f'<div style="text-align: center; padding: 15px;"><img src="data:image/png;base64,{get_base64_logo("logo.png")}" width="550"></div>', unsafe_allow_html=True)

# --- 6. Interfejs Główny ---
if map_selection == L["map_option_gold"]:
    st.subheader(f"🗺️ {L['map_option_gold']}")
    gold_data = {'ISO_Code': ['USA', 'DEU', 'ITA', 'FRA', 'RUS', 'CHN', 'CHE', 'JPN', 'IND', 'POL'], 'Tons': [8133, 3352, 2451, 2436, 2332, 2264, 1040, 846, 822, 359]}
    fig = px.choropleth(pd.DataFrame(gold_data), locations="ISO_Code", color="Tons", color_continuous_scale=px.colors.diverging.RdYlGn)
    st.plotly_chart(fig, use_container_width=True)
else:
    c1, c2 = st.columns(2)
    with c1: selected_country = st.selectbox("📍 Państwo:", ALL_COUNTRIES)
    with c2:
        if analysis_mode == L["mode_res"]: target = st.selectbox("💎 Surowiec:", COMMODITIES)
        elif analysis_mode == L["mode_pol"]: target = st.selectbox("🏛️ Obszar:", ["System Władzy", "Partie Polityczne", "Główni Liderzy"])
        else: target = st.selectbox("🤝 Partner:", ALL_COUNTRIES, index=1)

    # --- SEKCHJA QUICK STATS (TYLKO DLA SUROWCÓW) ---
    if analysis_mode == L["mode_res"]:
        st.markdown("---")
        # Pobieranie danych ze słownika lub ustawienie placeholderów
        stats = COUNTRY_STATS.get(selected_country, {"gdp": "Pobieranie...", "pop": "Pobieranie..."})
        
        s1, s2 = st.columns(2)
        metric_gdp = s1.metric(L["stat_gdp"], stats["gdp"])
        metric_pop = s2.metric(L["stat_pop"], stats["pop"])

    # --- GENEROWANIE RAPORTU ---
    if st.button(L["btn_gen"], use_container_width=True):
        if not api_key: st.error("Wpisz klucz API!")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner(L["loading"]):
                # Jeśli tryb to surowce, prosimy AI najpierw o krótkie dane statystyczne do odświeżenia metryk
                prompt = f"Stwórz raport geopolityczny dla {selected_country} w kontekście {target}. Tryb: {analysis_mode}. Język: {L['code']}. Bez hashtagów."
                
                # Opcjonalnie: Jeśli PKB/Pop jest nieznane, AI może je zwrócić w pierwszej linii (uproszczenie)
                resp = client.chat.completions.create(model=model_version, messages=[{"role": "user", "content": prompt}])
                
                st.markdown(f'<div class="report-card"><h3>{selected_country} | {target}</h3>{resp.choices[0].message.content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

st.markdown("---")
st.write(f"© 2024 GeoCommodity Insights | {L['footer']}")
