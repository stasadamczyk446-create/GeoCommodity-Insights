import streamlit as st
from openai import OpenAI
import os
import base64

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. PEŁNA BAZA PAŃSTW ŚWIATA (195+) ---
ALL_COUNTRIES = sorted([
    "Afganistan", "Albania", "Algieria", "Andora", "Angola", "Antigua i Barbuda", "Arabia Saudyjska", "Argentyna", "Armenia", "Australia", 
    "Austria", "Azerbejdżan", "Bahamy", "Bahrajn", "Bangladesz", "Barbados", "Belgia", "Belize", "Benin", "Bhutan", "Białoruś", "Boliwia", 
    "Bośnia i Hercegowina", "Botswana", "Brazylia", "Brunei", "Bułgaria", "Burkina Faso", "Burundi", "Chile", "Chiny", "Chorwacja", "Cypr", 
    "Czad", "Czarnogóra", "Czechy", "Dania", "Demokratyczna Republika Konga", "Dominika", "Dominikana", "Dżibuti", "Egipt", "Ekwador", 
    "Erytrea", "Estonia", "Eswatini", "Etiopia", "Fidżi", "Filipiny", "Finlandia", "Francja", "Gabon", "Gambia", "Ghana", "Grecja", 
    "Grenada", "Gruzja", "Gujana", "Gwatemala", "Gwinea", "Gwinea Bissau", "Gwinea Równikowa", "Haiti", "Hiszpania", "Holandia", "Honduras", 
    "Indie", "Indonezja", "Irak", "Iran", "Irlandia", "Islandia", "Izrael", "Jamajka", "Japonia", "Jemen", "Jordania", "Kambodża", "Kamerun", 
    "Kanada", "Katar", "Kazachstan", "Kenia", "Kirgistan", "Kiribati", "Kolumbia", "Komory", "Kongo", "Korea Południowa", "Korea Północna", 
    "Kostaryka", "Kuba", "Kuwejt", "Laos", "Lesotho", "Liban", "Liberia", "Libia", "Liechtenstein", "Litwa", "Luksemburg", "Łotwa", 
    "Macedonia Północna", "Madagaskar", "Malawi", "Malediwy", "Malezja", "Mali", "Malta", "Maroko", "Mauretania", "Mauritius", "Meksyk", 
    "Mikronezja", "Birma (Myanmar)", "Mołdawia", "Monako", "Mongolia", "Mozambik", "Namibia", "Nauru", "Nepal", "Niemcy", "Niger", 
    "Nigeria", "Nikaragua", "Norwegia", "Nowa Zelandia", "Oman", "Pakistan", "Palau", "Panama", "Papua-Nowa Gwinea", "Paragwaj", "Peru", 
    "Polska", "Portugalia", "Republika Środkowoafrykańska", "Republika Południowej Afryki", "Rosja", "Rumunia", "Rwanda", "Saint Kitts i Nevis", 
    "Saint Lucia", "Saint Vincent i Grenadyny", "Salwador", "Samoa", "San Marino", "Senegal", "Serbia", "Seszele", "Sierra Leone", 
    "Singapur", "Słowacja", "Słowenia", "Somalia", "Sri Lanka", "Sudan", "Surinam", "Syria", "Szwajcaria", "Szwecja", "Tadżykistan", 
    "Tajlandia", "Tajwan", "Tanzania", "Togo", "Tonga", "Trynidad i Tobago", "Tunezja", "Turcja", "Turkmenistan", "Tuvalu", "Uganda", 
    "Ukraina", "Urugwaj", "USA", "Uzbekistan", "Vanuatu", "Watykan", "Wenezuela", "Węgry", "Wielka Brytania", "Wietnam", "Włochy", 
    "Wybrzeże Kości Słoniowej", "Wyspy Marshalla", "Wyspy Salomona", "Zambia", "Zimbabwe", "Zjednoczone Emiraty Arabskie"
])

# --- 3. ROZSZERZONA LISTA SUROWCÓW (25+) ---
COMMODITIES = sorted([
    # Energetyka
    "Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór",
    # Metale Przemysłowe i Szlachetne
    "Miedź", "Aluminium", "Żelazo", "Nikiel", "Cynk", "Złoto", "Srebro", "Platyna", "Pallad",
    # Surowce Krytyczne i Technologiczne
    "Lit", "Kobalt", "Metale Ziem Rzadkich", "Grafit", "Krzem", "Magnez",
    # Rolnictwo
    "Pszenica (Zboże)", "Kukurydza", "Rzepak", "Ryż", "Kawa", "Kauczuk"
])

# --- 4. Słownik Języków ---
LANG = {
    "Polski 🇵🇱": {
        "code": "PL",
        "slogan": "Strategiczna Analityka wspierana przez AI",
        "api_label": "Klucz API OpenAI",
        "mode_label": "Tryb analizy:",
        "mode_res": "Surowce Strategiczne",
        "mode_pol": "Partie Polityczne",
        "country_label": "📍 Wybierz Państwo:",
        "res_label": "💎 Wybierz Surowiec:",
        "pol_label": "🏛️ Wybierz Partię (lub wpisz):",
        "btn_gen": "🚀 GENERUJ RAPORT STRATEGICZNY",
        "loading": "Trwa analiza geopolityczna...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski"
    },
    "English 🇬🇧": {
        "code": "EN",
        "slogan": "AI-Powered Strategic Intelligence",
        "api_label": "OpenAI API Key",
        "mode_label": "Analysis Mode:",
        "mode_res": "Strategic Commodities",
        "mode_pol": "Political Parties",
        "country_label": "📍 Select Country:",
        "res_label": "💎 Select Commodity:",
        "pol_label": "🏛️ Select Party (or type):",
        "btn_gen": "🚀 GENERATE STRATEGIC REPORT",
        "loading": "Analyzing geopolitics...",
        "footer": "Educational Project - University of Warsaw"
    }
}

# --- 5. Sidebar ---
with st.sidebar:
    lang_display = st.selectbox("Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")
    api_key = st.text_input(L["api_label"], type="password")
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"]])
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])

# --- 6. Wyśrodkowane Logo (550px) ---
if os.path.exists("logo.png"):
    def get_base64_logo(file):
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    encoded_logo = get_base64_logo("logo.png")
    st.markdown(f"""
        <div style="display: flex; justify-content: center; padding-top: 25px;">
            <img src="data:image/png;base64,{encoded_logo}" width="550">
        </div>
        <p style="text-align: center; color: #555; margin-top: 20px; font-weight: 500; font-size: 1.1em;">{L['slogan']}</p>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"<h1 style='text-align: center;'>GeoCommodity Insights</h1>", unsafe_allow_html=True)

st.markdown("---")

# --- 7. Wybór danych ---
col1, col2 = st.columns(2)
with col1:
    selected_country = st.selectbox(L["country_label"], ALL_COUNTRIES)
with col2:
    if analysis_mode == L["mode_res"]:
        target_item = st.selectbox(L["res_label"], COMMODITIES)
    else:
        target_item = st.text_input(L["pol_label"], value="Główne siły polityczne")

# --- 8. Silnik AI ---
if st.button(L["btn_gen"], use_container_width=True):
    if not api_key:
        st.error("Proszę podać klucz API!")
    else:
        try:
            client = OpenAI(api_key=api_key)
            with st.spinner(L["loading"]):
                prompt = f"Analiza {analysis_mode} dla {selected_country} w odniesieniu do {target_item}. Język: {L['code']}."
                response = client.chat.completions.create(
                    model=model_version,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(f"""
                <div class="report-card">
                    <h2 style="color: #002d62; border-bottom: 2px solid #f0f2f6; padding-bottom: 15px;">
                        {selected_country} | {target_item}
                    </h2>
                    <div style="line-height: 1.7;">{response.choices[0].message.content.replace('\n', '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Błąd: {e}")

# --- 9. Stopka ---
st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size: 0.85em; color: #888;'>© 2024 GeoCommodity Insights | {L['footer']}</p>", unsafe_allow_html=True)