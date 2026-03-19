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

# --- 2. Baza danych (Państwa i Surowce) ---
ALL_COUNTRIES = sorted(["Afganistan", "Albania", "Algieria", "Arabia Saudyjska", "Argentyna", "Australia", "Austria", "Belgia", "Brazylia", "Chile", "Chiny", "Czechy", "Dania", "Egipt", "Francja", "Grecja", "Hiszpania", "Indie", "Indonezja", "Izrael", "Japonia", "Kanada", "Kazachstan", "Meksyk", "Niemcy", "Nigeria", "Norwegia", "Polska", "Portugalia", "RPA", "Rosja", "Szwajcaria", "Szwecja", "Turcja", "Ukraina", "USA", "Węgry", "Wielka Brytania", "Włochy", "ZEA"])
COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Miedź", "Lit", "Uran", "Węgiel", "Złoto", "Srebro", "Kobalt", "Metale Ziem Rzadkich", "Pszenica", "Kukurydza", "Nikiel", "Aluminium"])

# --- 3. Słownik Języków (Bez PL/GB) ---
LANG = {
    "Polski 🇵🇱": {
        "code": "Polish",
        "slogan": "Strategiczna Analityka oparta na danych IMF Article IV",
        "api_label": "Klucz API OpenAI",
        "mode_label": "Obszar analizy:",
        "mode_res": "Surowce Strategiczne",
        "mode_pol": "Scena Polityczna",
        "country_label": "📍 Wybierz Państwo:",
        "res_label": "💎 Wybierz Surowiec:",
        "pol_label": "🏛️ Podmiot polityczny:",
        "btn_gen": "🚀 GENERUJ RAPORT (IMF DATA SOURCE)",
        "loading": "Przeszukiwanie baz danych IMF Article IV...",
        "footer": "GeoCommodity Insights | Data Source: IMF Staff Reports & OpenAI"
    },
    "English 🇬🇧": {
        "code": "English",
        "slogan": "Strategic Analytics based on IMF Article IV Data",
        "api_label": "OpenAI API Key",
        "mode_label": "Analysis Mode:",
        "mode_res": "Strategic Commodities",
        "mode_pol": "Political Landscape",
        "country_label": "📍 Select Country:",
        "res_label": "💎 Select Commodity:",
        "pol_label": "🏛️ Political Entity:",
        "btn_gen": "🚀 GENERATE REPORT (IMF DATA SOURCE)",
        "loading": "Consulting IMF Article IV Staff Reports...",
        "footer": "GeoCommodity Insights | Data Source: IMF Staff Reports & OpenAI"
    }
}

# --- 4. Sidebar ---
with st.sidebar:
    lang_display = st.selectbox("Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")
    api_key = st.text_input(L["api_label"], type="password")
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"]])
    model_version = st.selectbox("Model:", ["gpt-4o-mini", "gpt-4o"])

# --- 5. Logo ---
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

st.markdown("---")

# --- 6. Interfejs ---
col1, col2 = st.columns(2)
with col1:
    selected_country = st.selectbox(L["country_label"], ALL_COUNTRIES)
with col2:
    if analysis_mode == L["mode_res"]:
        target_item = st.selectbox(L["res_label"], COMMODITIES)
    else:
        target_item = st.text_input(L["pol_label"], value="Główne partie i stabilność")

# --- 7. Silnik AI z metodologią IMF Article IV ---
if st.button(L["btn_gen"], use_container_width=True):
    if not api_key:
        st.error("Wprowadź klucz API!")
    else:
        try:
            client = OpenAI(api_key=api_key)
            with st.spinner(L["loading"]):
                
                prompt = f"""
                Analyze the following case using the framework of IMF Article IV Consultation reports:
                COUNTRY: {selected_country}
                SUBJECT: {target_item} ({analysis_mode})

                INSTRUCTIONS:
                1. Reference the latest macro-critical trends described in IMF Staff Reports for {selected_country}.
                2. Evaluate how {target_item} impacts fiscal sustainability and external sector stability.
                3. If analyzing political entities, focus on their impact on structural reforms and economic governance.
                4. Provide a 'Staff Appraisal' style summary.

                LANGUAGE: Respond entirely in {L['code']}.
                """

                response = client.chat.completions.create(
                    model=model_version,
                    messages=[
                        {"role": "system", "content": "You are a senior IMF economist specializing in geopolitical and commodity risks. Use official technical language."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                st.markdown(f"""
                <div class="report-card">
                    <h2 style="color: #002d62; border-bottom: 2px solid #f0f2f6; padding-bottom: 15px;">
                        Economic & Strategic Review: {selected_country}
                    </h2>
                    <div style="line-height: 1.7;">{response.choices[0].message.content.replace('\n', '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size: 0.8em; color: #888;'>{L['footer']}</p>", unsafe_allow_html=True)
