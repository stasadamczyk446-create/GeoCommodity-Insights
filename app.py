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
        font-size: 1.8rem;
        color: #002d62;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Baza Danych (Rozszerzona o Statystyki) ---
COUNTRY_STATS = {
    "Polska": {"gdp": "$680B", "pop": "38M", "export": "Maszyny/Auta"},
    "USA": {"gdp": "$25.5T", "pop": "333M", "export": "Technologia/Ropa"},
    "Chiny": {"gdp": "$17.9T", "pop": "1.4B", "export": "Elektronika"},
    "Niemcy": {"gdp": "$4.1T", "pop": "83M", "export": "Motoryzacja"},
    "Ukraina": {"gdp": "$160B", "pop": "37M", "export": "Zboże/Stal"},
    "Arabia Saudyjska": {"gdp": "$1.1T", "pop": "36M", "export": "Ropa Naftowa"},
    "Rosja": {"gdp": "$2.2T", "pop": "144M", "export": "Gaz/Ropa"},
    "Brazylia": {"gdp": "$1.9T", "pop": "214M", "export": "Ruda żelaza/Soja"},
    "Indie": {"gdp": "$3.4T", "pop": "1.4B", "export": "Software/Paliwa"},
    "Wielka Brytania": {"gdp": "$3.1T", "pop": "67M", "export": "Usługi/Finanse"}
}
# Domyślne wartości dla pozostałych krajów
DEFAULT_STATS = {"gdp": "Brak danych", "pop": "Brak danych", "export": "Analiza w toku"}

ALL_COUNTRIES = sorted(list(set(list(COUNTRY_STATS.keys()) + ["Afganistan", "Albania", "Algieria", "Francja", "Włochy", "Kazachstan", "Turcja", "ZEA", "Kanada", "Australia"])))
COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór", "Miedź", "Aluminium", "Lit", "Kobalt", "Złoto", "Pszenica"])

gold_data = {
    'Country': ['USA', 'Germany', 'Italy', 'France', 'Russia', 'China', 'Switzerland', 'Japan', 'India', 'Turkey', 'Poland'],
    'ISO_Code': ['USA', 'DEU', 'ITA', 'FRA', 'RUS', 'CHN', 'CHE', 'JPN', 'IND', 'TUR', 'POL'],
    'Tons': [8133, 3352, 2451, 2436, 2332, 2264, 1040, 846, 822, 584, 359]
}
df_gold = pd.DataFrame(gold_data)

# --- 3. Słownik Języków ---
LANG = {
    "Polska 🇵🇱": {
        "code": "PL",
        "slogan": "Strategiczna Analityka wspierana przez AI",
        "nav_analysis": "📂 ANALIZA TEKSTOWA",
        "nav_maps": "🗺️ MODUŁ WIZUALNY",
        "mode_label": "Wybierz tryb:",
        "stat_gdp": "PKB (Nominalne)",
        "stat_pop": "Populacja",
        "stat_exp": "Główny Eksport",
        "map_option_off": "Wyłączona",
        "map_option_gold": "Mapa Rezerw Złota",
        "btn_gen": "🚀 GENERUJ RAPORT",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski"
    },
    "English 🇬🇧": {
        "code": "EN",
        "slogan": "AI-Powered Strategic Intelligence",
        "nav_analysis": "📂 TEXTUAL ANALYSIS",
        "nav_maps": "🗺️ VISUAL MODULE",
        "mode_label": "Select mode:",
        "stat_gdp": "GDP (Nominal)",
        "stat_pop": "Population",
        "stat_exp": "Main Export",
        "map_option_off": "Disabled",
        "map_option_gold": "Gold Reserves Map",
        "btn_gen": "🚀 GENERATE REPORT",
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
    analysis_mode = st.radio(L["mode_label"], ["Surowce Strategiczne", "Polityka", "Analiza Relacji"])
    st.markdown("---")
    st.markdown(f"### {L['nav_maps']}")
    map_selection = st.selectbox(L["nav_maps"], [L["map_option_off"], L["map_option_gold"]])
    st.markdown("---")
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])

# --- 5. Logo ---
if os.path.exists("logo.png"):
    def get_base64_logo(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    st.markdown(f'<div style="text-align: center; padding: 20px;"><img src="data:image/png;base64,{get_base64_logo("logo.png")}" width="550"></div>', unsafe_allow_html=True)

# --- 6. Interfejs Główny ---
if map_selection == L["map_option_gold"]:
    st.subheader(f"🗺️ {L['map_option_gold']}")
    fig = px.choropleth(df_gold, locations="ISO_Code", color="Tons", hover_name="Country", color_continuous_scale=px.colors.diverging.RdYlGn)
    st.plotly_chart(fig, use_container_width=True)
else:
    col1, col2 = st.columns(2)
    with col1: selected_country = st.selectbox("📍 Wybierz Państwo:", ALL_COUNTRIES)
    with col2: 
        if analysis_mode == "Surowce Strategiczne": target = st.selectbox("💎 Surowiec:", COMMODITIES)
        elif analysis_mode == "Polityka": target = st.selectbox("🏛️ Obszar:", ["Partie", "System Władzy", "Liderzy"])
        else: target = st.selectbox("🤝 Drugie Państwo:", ALL_COUNTRIES, index=1)

    # --- SEKCHJA QUICK STATS ---
    stats = COUNTRY_STATS.get(selected_country, DEFAULT_STATS)
    st.markdown("#### 📊 Quick Stats")
    s1, s2, s3 = st.columns(3)
    s1.metric(L["stat_gdp"], stats["gdp"])
    s2.metric(L["stat_pop"], stats["pop"])
    s3.metric(L["stat_exp"], stats["export"])

    if st.button(L["btn_gen"], use_container_width=True):
        if not api_key: st.error("Brak klucza API!")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner("Analizowanie..."):
                prompt = f"Raport dla {selected_country} - {target} ({analysis_mode}). Bez hashtagów."
                resp = client.chat.completions.create(model=model_version, messages=[{"role": "user", "content": prompt}])
                st.markdown(f'<div class="report-card"><h3>{selected_country} | {target}</h3>{resp.choices[0].message.content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

st.markdown("---")
st.write(f"© 2024 GeoCommodity Insights | {L['footer']}")
