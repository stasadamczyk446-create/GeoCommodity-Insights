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
    .report-card {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #eee;
        margin-top: 20px;
        color: #1e1e1e;
        line-height: 1.6;
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
    /* Dynamiczne kolory paska postępu */
    .stProgress > div > div > div > div {
        background-color: var(--p-color);
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
    'Country': ['Ukraina', 'Rosja', 'Izrael', 'Palestyna', 'Syria', 'Jemen', 'Tajwan', 'Korea Północna', 'Iran', 'Afganistan', 'Somalia', 'Mali', 'Burkina Faso', 'Niger', 'DR Konga', 'Wenezuela', 'Argentyna', 'Turcja', 'Egipt', 'Pakistan', 'Liban', 'Meksyk', 'Mjanma'],
    'ISO_Code': ['UKR', 'RUS', 'ISR', 'PSE', 'SYR', 'YEM', 'TWN', 'PRK', 'IRN', 'AFG', 'SOM', 'MLI', 'BFA', 'NER', 'COD', 'VEN', 'ARG', 'TUR', 'EGY', 'PAK', 'LBN', 'MEX', 'MMR'],
    'Kategoria': ['Wojna', 'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Niestabilność Polityczna', 'Niestabilność Polityczna', 'Niestabilność Polityczna', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Konflikt zbrojny', 'Konflikt zbrojny']
}
df_threats = pd.DataFrame(threat_data)

color_map_threats = {
    'Wojna': '#e74c3c',
    'Konflikt zbrojny': '#c0392b',
    'Niestabilność Polityczna': '#e67e22',
    'Terroryzm': '#d35400',
    'Kryzys Gospodarczy': '#8e44ad'
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
        "api_label": "Klucz API OpenAI", "nav_analysis": "📂 ANALIZA TEKSTOWA",
        "nav_maps": "🗺️ MODUŁ WIZUALNY", "mode_label": "Wybierz tryb:",
        "mode_res": "Surowce Strategiczne", "mode_pol": "Polityka", "mode_rel": "Analiza Relacji",
        "map_option_off": "Wyłączony", "map_option_gold": "Mapa Rezerw Złota", "map_option_threats": "Globalny Monitor Zagrożeń",
        "country_label": "📍 Wybierz Państwo:", "country2_label": "🤝 Wybierz drugie Państwo:",
        "res_label": "💎 Wybierz Surowiec:", "pol_submode_label": "🔍 Obszar polityki:",
        "pol_options": ["Partie Polityczne", "System Władzy", "Główne Osoby w Państwie"],
        "btn_gen": "🚀 GENERUJ RAPORT", "status_wait": "Oczekiwanie na instrukcje",
        "status_work": "Generowanie raportu...", "loading": "Trwa analiza...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski",
        "score_label": "Wskaźnik Bezpieczeństwa Strategicznego (1-10):"
    },
    "English 🇬🇧": {
        "code": "EN", "slogan": "AI-Powered Strategic Intelligence",
        "api_label": "OpenAI API Key", "nav_analysis": "📂 TEXTUAL ANALYSIS",
        "nav_maps": "🗺️ VISUAL MODULE", "mode_label": "Select mode:",
        "mode_res": "Strategic Commodities", "mode_pol": "Politics", "mode_rel": "Relationship Analysis",
        "map_option_off": "Disabled", "map_option_gold": "Gold Reserves Map", "map_option_threats": "Global Threat Monitor",
        "country_label": "📍 Select Country:", "country2_label": "🤝 Select second Country:",
        "res_label": "💎 Select Commodity:", "pol_submode_label": "🔍 Politics area:",
        "pol_options": ["Political Parties", "Government System", "Key Figures"],
        "btn_gen": "🚀 GENERATE REPORT", "status_wait": "Ready & Waiting",
        "status_work": "Generating report...", "loading": "Analyzing...",
        "footer": "Educational Project - University of Warsaw",
        "score_label": "Strategic Security Score (1-10):"
    }
}

# --- 5. Sidebar ---
with st.sidebar:
    lang_display = st.selectbox("Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"], L["mode_rel"]])
    st.markdown("---")
    map_selection = st.selectbox(L["nav_maps"], [L["map_option_off"], L["map_option_gold"], L["map_option_threats"]])
    st.markdown("---")
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])
    api_key = st.text_input(L["api_label"], type="password")

# --- 6. Logo ---
if os.path.exists("logo.png"):
    def get_base64_logo(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    encoded_logo = get_base64_logo("logo.png")
    st.markdown(f'<div style="display: flex; justify-content: center; padding-top: 25px;"><img src="data:image/png;base64,{encoded_logo}" width="550"></div>', unsafe_allow_html=True)

status_placeholder = st.empty()
status_placeholder.markdown(f'<div class="status-container"><p class="status-text">{L["slogan"]} | <span class="status-highlight">{L["status_wait"]}</span></p></div>', unsafe_allow_html=True)
st.markdown("---")

# --- 7. Interfejs Główny ---
if map_selection == L["map_option_gold"]:
    st.subheader(f"{L['map_option_gold']} (Ton)")
    fig = px.choropleth(df_gold, locations="ISO_Code", color="Log_Tons", hover_name="Country",
                        hover_data={"Log_Tons": False, "Tons": True},
                        color_continuous_scale="Spectral_r", labels={'Log_Tons':'Skala Potęgi', 'Tons': 'Tony'})
    fig.update_layout(geo=dict(showframe=False, projection_type='natural earth'), margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

elif map_selection == L["map_option_threats"]:
    st.subheader(L["map_option_threats"])
    fig_threats = px.choropleth(df_threats, locations="ISO_Code", color="Kategoria", hover_name="Country",
                        color_discrete_map=color_map_threats, 
                        category_orders={"Kategoria": ["Wojna", "Konflikt zbrojny", "Niestabilność Polityczna", "Terroryzm", "Kryzys Gospodarczy"]},
                        labels={'Kategoria':''})
    fig_threats.update_layout(geo=dict(showframe=False, projection_type='natural earth'), margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_threats, use_container_width=True)

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
                        if score_val >= 9: color_hex = "#2ecc71"; status_txt = "Optymalny"
                        elif score_val >= 7: color_hex = "#3498db"; status_txt = "Stabilny"
                        elif score_val >= 4: color_hex = "#f1c40f"; status_txt = "Umiarkowane ryzyko"
                        else: color_hex = "#e74c3c"; status_txt = "Wysokie ryzyko"
                        st.markdown(f'<style>div[data-testid="stProgress"] > div > div > div > div {{ background-color: {color_hex} !important; }}</style>', unsafe_allow_html=True)
                        st.write(f"**{L['score_label']}**")
                        st.progress(score_val / 10)
                        st.markdown(f'<p style="color:{color_hex}; font-weight:bold; margin-top:-10px;">Status: {status_txt} ({score_val}/10)</p>', unsafe_allow_html=True)

                    st.markdown(f'<div class="report-card"><h3>{selected_country} | {target_item}</h3>{clean_report.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                status_placeholder.markdown(f'<div class="status-container"><p class="status-text">{L["slogan"]} | <span class="status-highlight">{L["status_wait"]}</span></p></div>', unsafe_allow_html=True)
            except Exception as e: st.error(f"Błąd: {e}")

st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size: 0.85em; color: #888;'>© 2026 GeoCommodity Insights | {L['footer']}</p>", unsafe_allow_html=True)
