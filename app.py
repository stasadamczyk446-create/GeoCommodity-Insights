import streamlit as st
from openai import OpenAI
import os
import base64
import plotly.express as px
import pandas as pd

# --- 1. Konfiguracja Strony ---
st.set_page_config(page_title="GeoCommodity Insights", layout="wide", page_icon="🌍")

# CSS: Wdrożenie Dark Mode i poprawka dla logo (Filtr Invert)
st.markdown("""
    <style>
    /* 1. Globalny Ciemny Motyw dla całej strony */
    .stApp {
        background-color: #121212; /* Bardzo ciemny szary/czarny */
        color: #e0e0e0; /* Jasnoszary tekst */
    }

    /* 2. Stylizacja karty raportu AI (Kontrastowe tło) */
    .report-card {
        background-color: #1e1e1e; /* Nieco jaśniejszy czarny dla karty */
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255,255,255,0.05); /* Delikatny, jasny cień */
        border: 1px solid #333; /* Ciemna ramka */
        margin-top: 20px;
        color: #e0e0e0; /* Jasny tekst wewnątrz karty */
    }
    
    /* 3. Poprawka dla nagłówków w raporcie */
    .report-card h2, .report-card h3 {
        color: #007bff; /* Niebieski akcent dla nagłówków (jak w oryginale, ale jaśniejszy) */
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }

    /* 4. KLUCZOWE: Poprawka dla Logo na ciemnym tle */
    /* Nakładamy filtr, który odwraca kolory (biały->czarny, czarny->biały) */
    /* i ustawia przezroczystość dla dawnego białego tła. */
    .stImage img {
        filter: invert(1) hue-rotate(180deg) brightness(1.2);
        mix-blend-mode: lighten; /* Sprawia, że dawne białe tło znika */
    }

    /* 5. Stylizacja Paska Statusu */
    .status-container {
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .status-text {
        color: #aaa; /* Szary tekst sloganu */
        font-weight: 500;
        font-size: 1.0em;
    }
    .status-highlight {
        color: #007bff; /* Jasnoniebieski status */
        font-weight: bold;
    }

    /* 6. Korekta dla elementów Streamlit w Dark Mode */
    /* Upewniamy się, że teksty w sidebarze i labelach są jasne */
    .st-emotion-cache-6qob1r, .st-emotion-cache-10trblm, .st-emotion-cache-16idsys {
        color: #e0e0e0 !important;
    }
    /* Paski postępu i spinnery */
    .stProgress > div > div > div > div {
        background-color: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Baza Danych (Bez zmian) ---
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

# Przykładowe dane do mapy rezerw złota
gold_data = {
    'Country': ['United States', 'Germany', 'Italy', 'France', 'Russia', 'China', 'Switzerland', 'Japan', 'India', 'Turkey', 'Netherlands', 'Poland', 'Saudi Arabia', 'Portugal', 'Kazakhstan', 'Uzbekistan', 'Brazil', 'United Kingdom', 'Spain', 'Austria', 'Australia'],
    'ISO_Code': ['USA', 'DEU', 'ITA', 'FRA', 'RUS', 'CHN', 'CHE', 'JPN', 'IND', 'TUR', 'NLD', 'POL', 'SAU', 'PRT', 'KAZ', 'UZB', 'BRA', 'GBR', 'ESP', 'AUT', 'AUS'],
    'Tons': [8133, 3352, 2451, 2436, 2332, 2264, 1040, 846, 822, 584, 612, 359, 323, 382, 309, 362, 129, 310, 281, 280, 79]
}
df_gold = pd.DataFrame(gold_data)

# --- 3. Słownik Języków ---
LANG = {
    "Polska 🇵🇱": {
        "code": "PL",
        "slogan": "Strategiczna Analityka wspierana przez AI",
        "api_label": "Klucz API OpenAI",
        "nav_analysis": "📂 ANALIZA TEKSTOWA",
        "nav_maps": "🗺️ MODUŁ WIZUALNY",
        "mode_label": "Wybierz tryb:",
        "mode_res": "Surowce Strategiczne",
        "mode_pol": "Polityka",
        "mode_rel": "Analiza Relacji",
        "map_option_off": "Wyłączony",
        "map_option_gold": "Mapa Rezerw Złota",
        "country_label": "📍 Wybierz Państwo:",
        "country2_label": "🤝 Wybierz drugie Państwo:",
        "res_label": "💎 Wybierz Surowiec:",
        "pol_submode_label": "🔍 Obszar polityki:",
        "pol_options": ["Partie Polityczne", "System Władzy", "Główne Osoby w Państwie"],
        "btn_gen": "🚀 GENERUJ RAPORT",
        "status_wait": "🤖 Oczekiwanie na instrukcje",
        "status_work": "⏳ Generowanie raportu...",
        "loading": "Trwa analiza...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski"
    },
    "English 🇬🇧": {
        "code": "EN",
        "slogan": "AI-Powered Strategic Intelligence",
        "api_label": "OpenAI API Key",
        "nav_analysis": "📂 TEXTUAL ANALYSIS",
        "nav_maps": "🗺️ VISUAL MODULE",
        "mode_label": "Select mode:",
        "mode_res": "Strategic Commodities",
        "mode_pol": "Politics",
        "mode_rel": "Relationship Analysis",
        "map_option_off": "Disabled",
        "map_option_gold": "Gold Reserves Map",
        "country_label": "📍 Select Country:",
        "country2_label": "🤝 Select second Country:",
        "res_label": "💎 Select Commodity:",
        "pol_submode_label": "🔍 Politics area:",
        "pol_options": ["Political Parties", "Government System", "Key Figures"],
        "btn_gen": "🚀 GENERATE REPORT",
        "status_wait": "🤖 Ready & Waiting",
        "status_work": "⏳ Generating report...",
        "loading": "Analyzing...",
        "footer": "Educational Project - University of Warsaw"
    }
}

# --- 4. Sidebar ---
with st.sidebar:
    lang_display = st.selectbox("Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    
    st.markdown("---")
    st.markdown(f"### {L['nav_analysis']}")
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"], L["mode_rel"]])
    
    st.markdown("---")
    st.markdown(f"### {L['nav_maps']}")
    map_selection = st.selectbox(L["nav_maps"], [L["map_option_off"], L["map_option_gold"]])
    
    st.markdown("---")
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])
    
    # KLUCZ API NA SAMYM DOLE (Bez zmian)
    api_key = st.text_input(L["api_label"], type="password")

# --- 5. Logo (550px) z poprawką CSS ---
if os.path.exists("logo.png"):
    def get_base64_logo(file):
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    encoded_logo = get_base64_logo("logo.png")
    # CSS automatycznie poprawi logo (Invert Filter)
    st.markdown(f"""<div style="display: flex; justify-content: center; padding-top: 25px;">
        <img src="data:image/png;base64,{encoded_logo}" width="550">
        </div>""", unsafe_allow_html=True)

# --- ZINTEGROWANY STATUS I SLOGAN (Bez zmian w logice) ---
status_placeholder = st.empty()
status_placeholder.markdown(f"""
    <div class="status-container">
        <p class="status-text">{L['slogan']} | <span class="status-highlight">{L["status_wait"]}</span></p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# --- 6. Interfejs Główny ---
if map_selection == L["map_option_gold"]:
    st.subheader(f"🗺️ {L['map_option_gold']}")
    fig = px.choropleth(df_gold, locations="ISO_Code", color="Tons", hover_name="Country",
                        color_continuous_scale=px.colors.diverging.RdYlGn,
                        range_color=[0, 2500],
                        labels={'Tons':'Gold (Tons)'})
    fig.update_layout(geo=dict(showframe=False, projection_type='equirectangular'), margin={"r":0,"t":0,"l":0,"b":0})
    # Wykresy plotly automatycznie dostosowują się do ciemnego motywu w nowym Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("*Source: World Gold Council Data (2024)*")
else:
    col1, col2 = st.columns(2)
    with col1:
        selected_country = st.selectbox(L["country_label"], ALL_COUNTRIES)
    with col2:
        if analysis_mode == L["mode_res"]:
            target_item = st.selectbox(L["res_label"], COMMODITIES)
        elif analysis_mode == L["mode_pol"]:
            target_item = st.selectbox(L["pol_submode_label"], L["pol_options"])
        else:
            target_item = st.selectbox(L["country2_label"], ALL_COUNTRIES, index=1)

    if st.button(L["btn_gen"], use_container_width=True):
        if not api_key: st.error("Podaj klucz API!")
        else:
            try:
                # Zmiana statusu na górze (Kolor złoty dla kontrastu)
                status_placeholder.markdown(f"""
                    <div class="status-container">
                        <p class="status-text">{L['slogan']} | <span class="status-highlight" style="color: #d4a017;">{L["status_work"]}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                client = OpenAI(api_key=api_key)
                with st.spinner(L["loading"]):
                    if analysis_mode == L["mode_res"]:
                        p = f"Analiza {target_item} w {selected_country}. Strategia i gospodarka."
                    elif analysis_mode == L["mode_pol"]:
                        p = f"Analiza {target_item} w {selected_country}. Skup się tylko na tym konkretnym obszarze."
                    else:
                        p = f"Relacje {selected_country} - {target_item}. Dyplomacja i gospodarka."
                    
                    resp = client.chat.completions.create(model=model_version,
                        messages=[{"role": "system", "content": f"Ekspert geopolityki. Język: {L['code']}. Bez hashtagów."},
                                  {"role": "user", "content": p}])
                    
                    # Wyświetlenie raportu w Dark Mode
                    st.markdown(f'<div class="report-card"><h2>{selected_country} | {target_item}</h2>{resp.choices[0].message.content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                
                # Powrót do statusu bazowego
                status_placeholder.markdown(f"""
                    <div class="status-container">
                        <p class="status-text">{L['slogan']} | <span class="status-highlight">{L["status_wait"]}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e: st.error(f"Błąd: {e}")

st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size: 0.85em; color: #888;'>© 2024 GeoCommodity Insights | {L['footer']}</p>", unsafe_allow_html=True)
