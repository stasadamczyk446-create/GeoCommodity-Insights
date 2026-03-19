import streamlit as st
from openai import OpenAI
import os
import base64
from fpdf import FPDF

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
    .spacer { margin-top: 40px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Baza Danych (Pozostaje bez zmian) ---
ALL_COUNTRIES = sorted(["Afganistan", "Albania", "Algieria", "Andora", "Angola", "Arabia Saudyjska", "Argentyna", "Armenia", "Australia", "Austria", "Azerbejdżan", "Bahamy", "Bahrajn", "Bangladesz", "Barbados", "Belgia", "Belize", "Benin", "Bhutan", "Białoruś", "Boliwia", "Bośnia i Hercegowina", "Botswana", "Brazylia", "Brunei", "Bułgaria", "Burkina Faso", "Burundi", "Chile", "Chiny", "Chorwacja", "Cypr", "Czad", "Czarnogóra", "Czechy", "Dania", "Egipt", "Ekwador", "Erytrea", "Estonia", "Etiopia", "Filipiny", "Finlandia", "Francja", "Gabon", "Gambia", "Ghana", "Grecja", "Gruzja", "Gwatemala", "Gwinea", "Haiti", "Hiszpania", "Holandia", "Honduras", "Indie", "Indonezja", "Irak", "Iran", "Irlandia", "Islandia", "Izrael", "Jamajka", "Japonia", "Jemen", "Jordania", "Kambodża", "Kamerun", "Kanada", "Katar", "Kazachstan", "Kenia", "Kirgistan", "Kolumbia", "Kongo", "Korea Południowa", "Korea Północna", "Kostaryka", "Kuba", "Kuwejt", "Laos", "Liban", "Liberia", "Libia", "Litwa", "Luksemburg", "Łotwa", "Macedonia Północna", "Madagaskar", "Malezja", "Malta", "Maroko", "Meksyk", "Mołdawia", "Monako", "Mongolia", "Mozambik", "Namibia", "Nepal", "Niemcy", "Niger", "Nigeria", "Nikaragua", "Norwegia", "Nowa Zelandia", "Oman", "Pakistan", "Panama", "Paragwaj", "Peru", "Polska", "Portugalia", "Republika Południowej Afryki", "Rosja", "Rumunia", "Rwanda", "Salwador", "Senegal", "Serbia", "Singapur", "Słowacja", "Słowenia", "Somalia", "Sri Lanka", "Sudan", "Surinam", "Syria", "Szwajcaria", "Szwecja", "Tadżykistan", "Tajlandia", "Tajwan", "Tanzania", "Tunezja", "Turcja", "Turkmenistan", "Uganda", "Ukraina", "Urugwaj", "USA", "Uzbekistan", "Wenezuela", "Węgry", "Wielka Brytania", "Wietnam", "Włochy", "Wybrzeże Kości Słoniowej", "Zambia", "Zimbabwe", "ZEA"])
COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór", "Miedź", "Aluminium", "Żelazo", "Nikiel", "Cynk", "Złoto", "Srebro", "Platyna", "Lit", "Kobalt", "Metale Ziem Rzadkich", "Grafit", "Krzem", "Magnez", "Pszenica (Zboże)", "Kukurydza", "Rzepak", "Ryż", "Kawa", "Kauczuk"])

# --- 3. Słownik Języków ---
LANG = {
    "Polska 🇵🇱": {
        "code": "PL",
        "slogan": "Strategiczna Analityka wspierana przez AI",
        "api_label": "Klucz API OpenAI",
        "mode_label": "Tryb analizy:",
        "mode_res": "Surowce Strategiczne",
        "mode_pol": "Polityka",
        "mode_rel": "Analiza Relacji",
        "country_label": "📍 Wybierz Państwo:",
        "country2_label": "🤝 Wybierz drugie Państwo:",
        "res_label": "💎 Wybierz Surowiec:",
        "pol_submode_label": "🔍 Obszar polityki:",
        "pol_options": ["Partie Polityczne", "System Władzy", "Główne Osoby w Państwie"],
        "btn_gen": "🚀 GENERUJ RAPORT STRATEGICZNY",
        "btn_pdf": "📥 Pobierz raport PDF",
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
        "country_label": "📍 Select Country:",
        "country2_label": "🤝 Select second Country:",
        "res_label": "💎 Select Commodity:",
        "pol_submode_label": "🔍 Politics area:",
        "pol_options": ["Political Parties", "Government System", "Key Figures"],
        "btn_gen": "🚀 GENERATE STRATEGIC REPORT",
        "btn_pdf": "📥 Download PDF Report",
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
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"], L["mode_rel"]])
    model_version = st.selectbox("Model AI:", ["gpt-4o-mini", "gpt-4o"])

# --- 5. Logo Główne (550px) ---
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

# --- 6. Wybór danych ---
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

# --- 7. Poprawiona Funkcja PDF (Odporna na błędy formatu logo) ---
def create_pdf(title, content, footer_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Próba dodania Logo do PDF
    if os.path.exists("logo.png"):
        try:
            # Używamy bezpośredniej ścieżki, ale w bloku try
            pdf.image("logo.png", x=70, y=10, w=70)
            pdf.ln(40) 
        except Exception:
            # Jeśli format PNG jest zły, pomijamy logo i dajemy tylko odstęp
            pdf.ln(10)
            st.warning("Uwaga: Format pliku logo.png jest niekompatybilny z PDF. Raport wygenerowano bez logo.")
    
    # Tytuł
    pdf.set_font("Arial", 'B', 16)
    # Usuwamy polskie znaki tylko z tytułu dla stabilności
    clean_title = title.replace('ł','l').replace('ó','o').replace('ą','a').replace('ć','c').replace('ę','e').replace('ń','n').replace('ś','s').replace('ź','z').replace('ż','z')
    pdf.cell(0, 10, clean_title, ln=True, align='C')
    pdf.ln(10)
    
    # Treść raportu
    pdf.set_font("Arial", size=11)
    
    # Kodowanie latin-1 z ignorowaniem błędów (najstabilniejsze dla FPDF)
    safe_content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, safe_content)
    
    # Stopka
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 8)
    clean_footer = footer_text.replace('ł','l').replace('ó','o').replace('ą','a').replace('ć','c').replace('ę','e').replace('ń','n').replace('ś','s').replace('ź','z').replace('ż','z')
    pdf.cell(0, 10, clean_footer, 0, 0, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- 8. Silnik AI ---
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
                    messages=[
                        {"role": "system", "content": f"Jesteś profesjonalnym analitykiem geopolitycznym. Odpowiadaj w języku: {L['code']}. Pod żadnym pozorem nie używaj hashtagów."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                report_text = response.choices[0].message.content
                header_title = f"{selected_country} + {target_item}" if analysis_mode == L["mode_rel"] else f"{selected_country} | {target_item}"
                
                # Wyświetlenie na stronie
                st.markdown(f"""
                <div class="report-card">
                    <h2 style="color: #002d62; border-bottom: 2px solid #f0f2f6; padding-bottom: 15px; margin-bottom: 20px;">
                        {header_title}
                    </h2>
                    <div style="line-height: 1.7;">{report_text.replace('\n', '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)

                # --- 9. Sekcja Pobierania (Przesunięta niżej) ---
                st.write("") # Pusta linia dla odstępu
                st.write("") # Druga pusta linia
                
                pdf_data = create_pdf(header_title, report_text, L["footer"])
                
                # Używamy kolumn, aby przycisk nie był na całą szerokość i wyglądał profesjonalnie
                col_left, col_mid, col_right = st.columns([1, 2, 1])
                with col_mid:
                    st.download_button(
                        label=L["btn_pdf"],
                        data=pdf_data,
                        file_name=f"Raport_{selected_country}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"Błąd: {e}")

# --- 10. Stopka ---
st.markdown("---")
st.markdown(f"<p style='text-align: center; font-size: 0.85em; color: #888;'>© 2024 GeoCommodity Insights | {L['footer']}</p>", unsafe_allow_html=True)
