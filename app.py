import streamlit as st
from openai import OpenAI
import os
import base64
import plotly.express as px
import pandas as pd
import json

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
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ececec;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Baza Danych ---
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

COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór", "Miedź", "Aluminium", "Lit", "Kobalt", "Złoto", "Srebro", "Nikiel"])

# --- 3. Funkcja pobierania danych dynamicznych ---
def get_quick_stats(country, api_key):
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"Podaj PKB nominalne (w USD, np. $680B lub $2.5T) oraz populację (np. 38M lub 1.4B) dla państwa: {country}. Odpowiedz TYLKO w formacie JSON: {{\"gdp\": \"...\", \"pop\": \"...\"}}"
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Używamy tańszego modelu do szybkich danych
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"gdp": "N/A", "pop": "N/A"}

# --- 4. Sidebar ---
with st.sidebar:
    st.header("Konfiguracja")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("---")
    analysis_mode = st.radio("Tryb analizy:", ["Surowce Strategiczne", "Polityka", "Analiza Relacji"])
    st.markdown("---")
    map_selection = st.selectbox("Moduł wizualny:", ["Wyłączony", "Mapa Rezerw Złota"])
    model_version = st.selectbox("Model AI do raportów:", ["gpt-4o-mini", "gpt-4o"])

# --- 5. Logo ---
if os.path.exists("logo.png"):
    def get_base64_logo(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    st.markdown(f'<div style="text-align: center; padding: 20px;"><img src="data:image/png;base64,{get_base64_logo("logo.png")}" width="550"></div>', unsafe_allow_html=True)

# --- 6. Interfejs Główny ---
if map_selection == "Mapa Rezerw Złota":
    st.subheader("🗺️ Globalne Rezerwy Złota")
    # (Tutaj zostaje kod mapy z poprzedniej wersji...)
    st.info("Mapa w trybie pełnoekranowym.")
else:
    col1, col2 = st.columns(2)
    
    with col1:
        selected_country = st.selectbox("📍 Wybierz Państwo:", ALL_COUNTRIES)
        
        # Sekcja Quick Stats PRZENIESIONA pod wybór państwa (Tylko dla surowców)
        if analysis_mode == "Surowce Strategiczne" and api_key:
            stats = get_quick_stats(selected_country, api_key)
            s1, s2 = st.columns(2)
            s1.metric("PKB (Nominal)", stats["gdp"])
            s2.metric("Populacja", stats["pop"])
        elif analysis_mode == "Surowce Strategiczne" and not api_key:
            st.caption("Wpisz klucz API, aby zobaczyć statystyki.")

    with col2:
        if analysis_mode == "Surowce Strategiczne":
            target = st.selectbox("💎 Wybierz Surowiec:", COMMODITIES)
        elif analysis_mode == "Polityka":
            target = st.selectbox("🏛️ Obszar analizy:", ["System Władzy", "Partie Polityczne", "Główni Liderzy"])
        else:
            target = st.selectbox("🤝 Wybierz Partnera:", ALL_COUNTRIES, index=1)

    # --- Przycisk Generowania ---
    if st.button("🚀 GENERUJ RAPORT STRATEGICZNY", use_container_width=True):
        if not api_key:
            st.error("Wymagany klucz API OpenAI.")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner("Sztuczna inteligencja analizuje dane geopolityczne..."):
                prompt = f"Stwórz profesjonalny raport geopolityczny dla państwa {selected_country} w kontekście {target}. Tryb: {analysis_mode}. Nie używaj hashtagów."
                resp = client.chat.completions.create(model=model_version, messages=[{"role": "user", "content": prompt}])
                
                st.markdown(f"""
                <div class="report-card">
                    <h2 style="color: #002d62; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px;">{selected_country} | {target}</h2>
                    <div style="margin-top: 20px;">{resp.choices[0].message.content.replace(chr(10), '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2024 GeoCommodity Insights | Projekt edukacyjny")
