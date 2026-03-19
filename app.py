import streamlit as st
from openai import OpenAI
import os
import base64
import plotly.express as px
import pandas as pd

# --- 1. Konfiguracja Strony ---
st.set_page_config(page_title="GeoCommodity Insights", layout="wide", page_icon="🌍")

# Stylizacja karty raportu (biały blok z cieniem)
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

# --- 2. Baza Danych (Państwa, Surowce, Dane do Mapy) ---
# ... (Pełna lista państw ALL_COUNTRIES zostaje bez zmian, pomijam dla czytelności kodu) ...
ALL_COUNTRIES = sorted(["Afganistan", "Albania", "Algieria", "Andora", "Angola", "Arabia Saudyjska", "Argentyna", "Armenia", "Australia", "Austria", "Azerbejdżan", "Bahamy", "Bahrajn", "Bangladesz", "Barbados", "Belgia", "Belize", "Benin", "Bhutan", "Białoruś", "Boliwia", "Bośnia i Hercegowina", "Botswana", "Brazylia", "Brunei", "Bułgaria", "Burkina Faso", "Burundi", "Chile", "Chiny", "Chorwacja", "Cypr", "Czad", "Czarnogóra", "Czechy", "Dania", "Egipt", "Ekwador", "Erytrea", "Estonia", "Etiopia", "Filipiny", "Finlandia", "Francja", "Gabon", "Gambia", "Ghana", "Grecja", "Gruzja", "Gwatemala", "Gwinea", "Haiti", "Hiszpania", "Holandia", "Honduras", "Indie", "Indonezja", "Irak", "Iran", "Irlandia", "Islandia", "Izrael", "Jamajka", "Japonia", "Jemen", "Jordania", "Kambodża", "Kamerun", "Kanada", "Katar", "Kazachstan", "Kenia", "Kirgistan", "Kolumbia", "Kongo", "Korea Południowa", "Korea Północna", "Kostaryka", "Kuba", "Kuwejt", "Laos", "Liban", "Liberia", "Libia", "Litwa", "Luksemburg", "Łotwa", "Macedonia Północna", "Madagaskar", "Malezja", "Malta", "Maroko", "Meksyk", "Mołdawia", "Monako", "Mongolia", "Mozambik", "Namibia", "Nepal", "Niemcy", "Niger", "Nigeria", "Nikaragua", "Norwegia", "Nowa Zelandia", "Oman", "Pakistan", "Panama", "Paragwaj", "Peru", "Polska", "Portugalia", "Republika Południowej Afryki", "Rosja", "Rumunia", "Rwanda", "Salwador", "Senegal", "Serbia", "Singapur", "Słowacja", "Słowenia", "Somalia", "Sri Lanka", "Sudan", "Syria", "Szwajcaria", "Szwecja", "Tadżykistan", "Tajlandia", "Tajwan", "Tanzania", "Tunezja", "Turcja", "Turkmenistan", "Uganda", "Ukraina", "Urugwaj", "USA", "Uzbekistan", "Wenezuela", "Węgry", "Wielka Brytania", "Wietnam", "Włochy", "Wybrzeże Kości Słoniowej", "Zambia", "Zimbabwe", "ZEA"])

COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór", "Miedź", "Aluminium", "Żelazo", "Nikiel", "Cynk", "Złoto", "Srebro", "Platyna", "Lit", "Kobalt", "Metale Ziem Rzadkich", "Grafit", "Krzem", "Magnez", "Pszenica (Zboże)", "Kukurydza", "Rzepak", "Ryż", "Kawa", "Kauczuk"])

# Przykładowe dane do mapy rezerw złota (w tonach, oparte na danych World Gold Council 2023/2024)
# Używamy nazw angielskich dla kompatybilności z mapą
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
        "mode_label": "Obszar analizy:",
        "mode_res": "Surowce Strategiczne",
        "mode_pol": "Polityka",
        "mode_rel": "Analiza Relacji",
        "mode_map": "Mapy Interaktywne",
        "country_label": "📍 Wybierz Państwo:",
        "country2_label": "🤝 Wybierz drugie Państwo:",
        "res_label": "💎 Wybierz Surowiec:",
        "pol_submode_label": "🔍 Obszar polityki:",
        "pol_options": ["Partie Polityczne", "System Władzy", "Główne Osoby w Państwie"],
        "map_label": "🗺️ Wybierz Mapę:",
        "map_gold": "Rezerwy Złota (Tonaż)",
        "map_gold_desc": "Globalny tonaż rezerw złota w posiadaniu banków centralnych.",
        "btn_gen": "🚀 GENERUJ RAPORT STRATEGICZNY",
        "btn_show_map": "🗺️ POKAŻ MAPĘ",
        "loading": "Trwa analiza geopolityczna...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski"
    },
    "English 🇬🇧": {
        "code": "EN",
        "slogan": "AI-Powered Strategic Intelligence",
        "api_label": "OpenAI API Key",
        "mode_label": "Analysis Mode:",
        "mode_res": "Strategic Commodities",
        "mode_pol": "Politics",
        "mode_rel": "Relationship Analysis",
        "mode_map": "Interactive Maps",
        "country_label": "📍 Select Country:",
        "country2_label": "🤝 Select second Country:",
        "res_label": "💎 Select Commodity:",
        "pol_submode_label": "🔍 Politics area:",
        "pol_options": ["Political Parties", "Government System", "Key Figures"],
        "map_label": "🗺️ Select Map:",
        "map_gold": "Gold Reserves (Tonnage)",
        "map_gold_desc": "Global gold reserve tonnage held by central banks.",
        "btn_gen": "🚀 GENERATE STRATEGIC REPORT",
        "btn_show_map": "🗺️ SHOW MAP",
        "loading": "Analyzing geopolitics...",
        "footer": "Educational Project - University of Warsaw"
    }
}

# --- 4. Sidebar ---
with st.sidebar:
    lang_display = st.selectbox("Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")
    api_key = st.text_input(L["api_label"], type="password")
    # Nowe menu z trybem map
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"], L["mode_rel"], L["mode_map"]])
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])

# --- 5. Logo (550px) ---
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
    st.markdown(f"<h1 style='text-align: center;'>{L['slogan']}</h1>", unsafe_allow_html=True)

st.markdown("---")

# --- 6. Interfejs Główny ---
# Tryb Map
if analysis_mode == L["mode_map"]:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_map = st.selectbox(L["map_label"], [L["map_gold"]])
        st.markdown(f"**{selected_map}**")
        st.markdown(L["map_gold_desc"])
        
        show_map = st.button(L["btn_show_map"], use_container_width=True)

    with col2:
        if show_map:
            if selected_map == L["map_gold"]:
                with st.spinner("Generowanie mapy..."):
                    
                    # Generowanie mapy za pomocą Plotly
                    fig = px.choropleth(df_gold, 
                                        locations="ISO_Code",
                                        color="Tons", 
                                        hover_name="Country",
                                        color_continuous_scale=px.colors.diverging.RdYlGn,
                                        # range_color=[0, df_gold['Tons'].max()], # Pełna skala
                                        range_color=[0, 3000], # Skala ucięta, aby kraje <3000 (np. Polska) były bardziej zielone
                                        title=f"Global Gold Reserves (Tons)",
                                        labels={'Tons':'Tons of Gold'}
                                       )
                    
                    fig.update_layout(
                        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
                        margin={"r":0,"t":40,"l":0,"b":0},
                        coloraxis_colorbar=dict(title="Gold (Tons)")
                    )
                    
                    # Wyświetlenie mapy w interfejsie Streamlit
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("*Źródło danych: World Gold Council (Q1 2024)*")

# Tryby Analityczne AI (Pozostają bez zmian)
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
            # Tryb Analizy Relacji - wybór drugiego kraju
            target_item = st.selectbox(L["country2_label"], ALL_COUNTRIES, index=1)

    # --- 7. Silnik AI ---
    if st.button(L["btn_gen"], use_container_width=True):
        if not api_key:
            st.error("Proszę podać klucz API!")
        else:
            try:
                client = OpenAI(api_key=api_key)
                with st.spinner(L["loading"]):
                    
                    if analysis_mode == L["mode_res"]:
                        prompt = f"Sporządź raport na temat surowca {target_item} w kraju {selected_country}. Skup się wyłącznie na aspekcie gospodarczym i strategicznym tego surowca. NIE UŻYWAJ HASHTAGÓW (#)."
                    elif analysis_mode == L["mode_pol"]:
                        prompt = f"Sporządź raport na temat: {target_item} w kraju {selected_country}. Skup się WYŁĄCZNIE na tym konkretnym obszarze polityki. NIE UŻYWAJ HASHTAGÓW (#)."
                    else:
                        prompt = f"Sporządź raport na temat relacji bilateralnych między {selected_country} a {target_item}. Opisz współpracę dyplomatyczną, gospodarczą oraz ewentualne punkty sporne. NIE UŻYWAJ HASHTAGÓW (#)."

                    response = client.chat.completions.create(
                        model=model_version,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    report_text = response.choices[0].message.content
                    header_title = f"{selected_country} + {target_item}" if analysis_mode == L["mode_rel"] else f"{selected_country} | {target_item}"
                    
                    st.markdown(f"""
                    <div class="report-card">
                        <h2 style="color: #002d62; border-bottom: 2px solid #f0f2f6; padding-bottom: 15px; margin-bottom: 20px;">
                            {header_title}
                        </h2>
                        <div style="line-height: 1.7;">{report_text.replace('\n', '<br>')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Błąd: {e}")

# --- 8. Stopka ---
st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size: 0.85em; color: #888;'>© 2024 GeoCommodity Insights | {L['footer']}</p>", unsafe_allow_html=True)
