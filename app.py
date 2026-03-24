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
    .status-container {
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .status-text {
        color: #555;
        font-weight: 500;
        font-size: 1.0em;
    }
    .status-highlight {
        color: #002d62;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Baza Danych Rezerw Złota ---
gold_data = {
    'Country': [
        'USA', 'Niemcy', 'Włochy', 'Francja', 'Rosja', 'Chiny', 'Szwajcaria', 'Japonia', 'Indie', 'Turcja', 
        'Holandia', 'Polska', 'Arabia Saudyjska', 'Portugalia', 'Kazachstan', 'Uzbekistan', 'Hiszpania', 
        'Austria', 'Tajlandia', 'Belgia', 'Algieria', 'Wenezuela', 'Filipiny', 'Brazylia', 'Singapur', 
        'Szwecja', 'RPA', 'Meksyk', 'Libia', 'Grecja', 'Korea Południowa', 'Rumunia', 'Egipt', 'Australia', 
        'Kuwejt', 'Indonezja', 'Katar', 'Pakistan', 'Argentyna', 'ZEA', 'Malezja',
        'Ukraina', 'Jordania', 'Słowacja', 'Węgry', 'Bułgaria', 'Białoruś', 'Finlandia', 'Serbia', 'Peru'
    ],
    'ISO_Code': [
        'USA', 'DEU', 'ITA', 'FRA', 'RUS', 'CHN', 'CHE', 'JPN', 'IND', 'TUR', 
        'NLD', 'POL', 'SAU', 'PRT', 'KAZ', 'UZB', 'ESP', 
        'AUT', 'THA', 'BEL', 'DZA', 'VEN', 'PHL', 'BRA', 'SGP', 
        'SWE', 'ZAF', 'MEX', 'LBY', 'GRC', 'KOR', 'ROU', 'EGY', 'AUS', 
        'KWT', 'IDN', 'QAT', 'PAK', 'ARG', 'ARE', 'MYS',
        'UKR', 'JOR', 'SVK', 'HUN', 'BGR', 'BLR', 'FIN', 'SRB', 'PER'
    ],
    'Tons': [
        8133, 3352, 2451, 2436, 2332, 2264, 1040, 846, 822, 584, 
        612, 359, 323, 382, 309, 362, 281, 
        280, 244, 227, 173, 161, 155, 129, 230, 
        126, 125, 120, 116, 114, 104, 103, 126, 79, 
        79, 78, 106, 64, 61, 74, 45,
        27, 43, 31, 94, 40, 53, 49, 38, 34
    ]
}
df_gold = pd.DataFrame(gold_data)

# --- Pełna Lista Państw ---
ALL_COUNTRIES = sorted(df_gold['Country'].tolist() + [
    "Wielka Brytania", "Kanada", "Norwegia", "Nigeria", "Chile", "Argentyna", "Azerbejdżan", 
    "Belgia", "Czechy", "Dania", "Egipt", "Finlandia", "Grecja", "Hiszpania", "Holandia", 
    "Irak", "Iran", "Izrael", "Katar", "Kolumbia", "Kuwejt", "Meksyk", "Nowa Zelandia", 
    "Oman", "Pakistan", "Portugalia", "Rumunia", "Słowacja", "Szwajcaria", "Szwecja", 
    "Tajwan", "Ukraina", "Wenezuela", "Węgry", "Wietnam", "Włochy"
])

# --- Pełna Lista Surowców (Przywrócona) ---
COMMODITIES = sorted([
    "Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór",
    "Miedź", "Aluminium", "Żelazo", "Nikiel", "Cynk", "Złoto", "Srebro", "Platyna",
    "Lit", "Kobalt", "Metale Ziem Rzadkich", "Grafit", "Krzem", "Magnez",
    "Pszenica (Zboże)", "Kukurydza", "Rzepak", "Ryż", "Kawa", "Kauczuk"
])

# --- 3. Słownik Języków ---
LANG = {
    "Polska 🇵🇱": {
        "code": "PL", "slogan": "Strategiczna Analityka wspierana przez AI",
        "api_label": "Klucz API OpenAI", "nav_analysis": "📂 ANALIZA TEKSTOWA",
        "nav_maps": "🗺️ MODUŁ WIZUALNY", "mode_label": "Wybierz tryb:",
        "mode_res": "Surowce Strategiczne", "mode_pol": "Polityka", "mode_rel": "Analiza Relacji",
        "map_option_off": "Wyłączony", "map_option_gold": "Mapa Rezerw Złota",
        "country_label": "📍 Wybierz Państwo:", "country2_label": "🤝 Wybierz drugie Państwo:",
        "res_label": "💎 Wybierz Surowiec:", "pol_submode_label": "🔍 Obszar polityki:",
        "pol_options": ["Partie Polityczne", "System Władzy", "Główne Osoby w Państwie"],
        "btn_gen": "🚀 GENERUJ RAPORT", "status_wait": "🤖 Oczekiwanie na instrukcje",
        "status_work": "⏳ Generowanie raportu...", "loading": "Trwa analiza...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski"
    },
    "English 🇬🇧": {
        "code": "EN", "slogan": "AI-Powered Strategic Intelligence",
        "api_label": "OpenAI API Key", "nav_analysis": "📂 TEXTUAL ANALYSIS",
        "nav_maps": "🗺️ VISUAL MODULE", "mode_label": "Select mode:",
        "mode_res": "Strategic Commodities", "mode_pol": "Politics", "mode_rel": "Relationship Analysis",
        "map_option_off": "Disabled", "map_option_gold": "Gold Reserves Map",
        "country_label": "📍 Select Country:", "country2_label": "🤝 Select second Country:",
        "res_label": "💎 Select Commodity:", "pol_submode_label": "🔍 Politics area:",
        "pol_options": ["Political Parties", "Government System", "Key Figures"],
        "btn_gen": "🚀 GENERATE REPORT", "status_wait": "🤖 Ready & Waiting",
        "status_work": "⏳ Generating report...", "loading": "Analyzing...",
        "footer": "Educational Project - University of Warsaw"
    }
}

# --- 4. Sidebar ---
with st.sidebar:
    lang_display = st.selectbox("Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"], L["mode_rel"]])
    st.markdown("---")
    map_selection = st.selectbox(L["nav_maps"], [L["map_option_off"], L["map_option_gold"]])
    st.markdown("---")
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])
    api_key = st.text_input(L["api_label"], type="password")

# --- 5. Logo ---
if os.path.exists("logo.png"):
    def get_base64_logo(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    encoded_logo = get_base64_logo("logo.png")
    st.markdown(f"""<div style="display: flex; justify-content: center; padding-top: 25px;">
        <img src="data:image/png;base64,{encoded_logo}" width="550">
        </div>""", unsafe_allow_html=True)

status_placeholder = st.empty()
status_placeholder.markdown(f'<div class="status-container"><p class="status-text">{L["slogan"]} | <span class="status-highlight">{L["status_wait"]}</span></p></div>', unsafe_allow_html=True)
st.markdown("---")

# --- 6. Interfejs Główny ---
if map_selection == L["map_option_gold"]:
    st.subheader(f"🗺️ {L['map_option_gold']} (Ton)")
    fig = px.choropleth(df_gold, 
                        locations="ISO_Code", 
                        color="Tons", 
                        hover_name="Country",
                        color_continuous_scale="Geyser", # Nowa, bardziej prestiżowa paleta kolorów
                        labels={'Tons':'Złoto (Tony)'})
    fig.update_layout(geo=dict(showframe=False, projection_type='natural earth'), 
                      margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
    st.info("Mapa pokazuje rezerwy dla 50 największych posiadaczy złota na świecie.")
else:
    col1, col2 = st.columns(2)
    with col1: selected_country = st.selectbox(L["country_label"], ALL_COUNTRIES)
    with col2:
        if analysis_mode == L["mode_res"]: target_item = st.selectbox(L["res_label"], COMMODITIES)
        elif analysis_mode == L["mode_pol"]: target_item = st.selectbox(L["pol_submode_label"], L["pol_options"])
        else: target_item = st.selectbox(L["country2_label"], ALL_COUNTRIES, index=1)

    if st.button(L["btn_gen"], use_container_width=True):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                status_placeholder.markdown(f'<div class="status-container"><p class="status-text">{L["slogan"]} | <span class="status-highlight" style="color: #d4a017;">{L["status_work"]}</span></p></div>', unsafe_allow_html=True)
                client = OpenAI(api_key=api_key)
                with st.spinner(L["loading"]):
                    prompt = f"Analiza {target_item} w {selected_country}. {analysis_mode}."
                    resp = client.chat.completions.create(model=model_version,
                        messages=[{"role": "system", "content": f"Jesteś ekspertem geopolityki. Odpowiadasz w języku: {L['code']}."},
                                  {"role": "user", "content": prompt}])
                    st.markdown(f'<div class="report-card"><h2>{selected_country} | {target_item}</h2>{resp.choices[0].message.content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                status_placeholder.markdown(f'<div class="status-container"><p class="status-text">{L["slogan"]} | <span class="status-highlight">{L["status_wait"]}</span></p></div>', unsafe_allow_html=True)
            except Exception as e: st.error(f"Błąd: {e}")

st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size: 0.85em; color: #888;'>© 2024 GeoCommodity Insights | {L['footer']}</p>", unsafe_allow_html=True)
