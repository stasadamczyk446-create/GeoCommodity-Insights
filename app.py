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
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, .brand-title {
        font-family: 'Poppins', sans-serif !important;
    }

    /* --- Tło aplikacji --- */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #1b2440 0%, transparent 45%),
                    radial-gradient(circle at 85% 85%, #241b40 0%, transparent 45%),
                    linear-gradient(160deg, #0b0f1e 0%, #10152b 50%, #0b0f1e 100%);
        background-attachment: fixed;
    }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1226 0%, #131a33 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #c7cde3 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08);
    }

    /* --- Sidebar header --- */
    .sidebar-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.05em;
        color: #f0f2ff;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sidebar-sub {
        color: #7b83a8 !important;
        font-size: 0.78em;
        margin-bottom: 14px;
    }

    /* --- Inputy / selecty --- */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    .stTextInput input {
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #f0f2ff !important;
    }
    div[data-baseweb="select"]:hover > div {
        border-color: rgba(120,140,255,0.5) !important;
    }
    .stTextInput input {
        color: #f0f2ff !important;
    }

    /* --- Radio jako "pill tabs" z podświetleniem aktywnej opcji --- */
    div[role="radiogroup"] {
        background: rgba(255,255,255,0.04);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        gap: 6px !important;
    }
    div[role="radiogroup"] label {
        background: rgba(255,255,255,0.02);
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 10px 12px !important;
        transition: all 0.2s ease;
        cursor: pointer;
        width: 100%;
    }
    div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(255,255,255,0.12);
    }
    /* Aktywna (zaznaczona) opcja - wyraźne podświetlenie indygo */
    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(99,102,241,0.22), rgba(168,85,247,0.16)) !important;
        border: 1px solid rgba(139,92,246,0.5) !important;
        box-shadow: 0 2px 10px rgba(139,92,246,0.15);
    }
    div[role="radiogroup"] label:has(input:checked) p {
        color: #f0f2ff !important;
        font-weight: 700 !important;
    }
    div[role="radiogroup"] label p {
        color: #a7afd1;
        font-weight: 500;
        transition: color 0.2s ease;
    }

    /* --- Hero header --- */
    .hero-wrap {
        text-align: center;
        padding: 10px 0 6px 0;
    }
    .brand-title {
        font-size: 2.6em;
        font-weight: 800;
        background: linear-gradient(90deg, #7dd3fc 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .brand-slogan {
        color: #8b93b8;
        font-size: 1.0em;
        font-weight: 500;
        margin-top: -8px;
    }

    /* --- Status pill --- */
    .status-container {
        text-align: center;
        margin-top: 14px;
        margin-bottom: 22px;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 20px;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 0.9em;
        font-weight: 500;
        color: #a7afd1;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4ade80;
        box-shadow: 0 0 8px #4ade80;
    }
    .status-dot.working {
        background: #fbbf24;
        box-shadow: 0 0 8px #fbbf24;
        animation: pulse 1.2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
    .status-highlight {
        color: #e4e7f7;
        font-weight: 700;
    }

    /* --- Karta wyboru (glass card) --- */
    .glass-card {
        background: rgba(255,255,255,0.045);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px;
        padding: 28px 30px;
        margin-bottom: 22px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    .glass-card-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.05em;
        color: #e4e7f7;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .glass-card-sub {
        color: #7b83a8;
        font-size: 0.85em;
        margin-bottom: 18px;
    }

    /* --- Report card --- */
    .report-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
        padding: 36px 38px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.09);
        margin-top: 22px;
        color: #dde1f5;
        line-height: 1.75;
        animation: fadeIn 0.6s ease;
    }
    .report-card h3 {
        color: #f0f2ff;
        border-bottom: 1px solid rgba(255,255,255,0.12);
        padding-bottom: 14px;
        margin-bottom: 18px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .report-card b {
        color: #a5b4fc;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- Przycisk generuj --- */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 0 !important;
        font-weight: 700 !important;
        font-family: 'Poppins', sans-serif !important;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 20px rgba(139,92,246,0.35);
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 28px rgba(139,92,246,0.55);
        transform: translateY(-2px);
    }

    /* --- Progress bar --- */
    .stProgress > div > div > div > div {
        background: var(--p-color);
        border-radius: 999px;
    }
    .stProgress > div > div > div {
        background-color: rgba(255,255,255,0.08) !important;
        border-radius: 999px;
    }

    /* --- Score badge --- */
    .score-badge-wrap {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 20px 24px;
        margin-top: 22px;
        backdrop-filter: blur(20px);
    }
    .score-title {
        color: #a7afd1;
        font-size: 0.85em;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }
    .score-status-text {
        font-weight: 700;
        margin-top: 10px;
        font-size: 0.95em;
    }

    /* --- Przyciski-kafelki wyglądające identycznie jak metric-card --- */
    /* Technika markera: div-znacznik tuż przed przyciskiem pozwala go precyzyjnie wybrać */
    div.element-container:has(div.metric-trigger-marker) + div.element-container button,
    div.element-container:has(div.metric-trigger-marker-2) + div.element-container button,
    div.element-container:has(div.metric-trigger-marker-3) + div.element-container button {
        border-radius: 16px !important;
        padding: 18px 20px !important;
        width: 100% !important;
        backdrop-filter: blur(20px);
        transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease !important;
        box-shadow: none !important;
        text-align: center !important;
        line-height: 1.35 !important;
        min-height: 96px;
    }
    /* Kafelek Państw - fioletowe tło + hover */
    div.element-container:has(div.metric-trigger-marker) + div.element-container button {
        background: rgba(139,92,246,0.16) !important;
        border: 1px solid rgba(139,92,246,0.3) !important;
    }
    div.element-container:has(div.metric-trigger-marker) + div.element-container button:hover {
        transform: translateY(-3px);
        border-color: rgba(139,92,246,0.55) !important;
        background: rgba(139,92,246,0.24) !important;
    }
    /* Kafelek Surowców - zielone tło + hover */
    div.element-container:has(div.metric-trigger-marker-2) + div.element-container button {
        background: rgba(34,197,94,0.14) !important;
        border: 1px solid rgba(34,197,94,0.3) !important;
    }
    div.element-container:has(div.metric-trigger-marker-2) + div.element-container button:hover {
        transform: translateY(-3px);
        border-color: rgba(34,197,94,0.55) !important;
        background: rgba(34,197,94,0.22) !important;
    }
    /* Kafelek Zagrożeń - czerwone tło + hover */
    div.element-container:has(div.metric-trigger-marker-3) + div.element-container button {
        background: rgba(239,68,68,0.16) !important;
        border: 1px solid rgba(239,68,68,0.3) !important;
    }
    div.element-container:has(div.metric-trigger-marker-3) + div.element-container button:hover {
        transform: translateY(-3px);
        border-color: rgba(239,68,68,0.55) !important;
        background: rgba(239,68,68,0.24) !important;
    }
    div.element-container:has(div.metric-trigger-marker) + div.element-container button p,
    div.element-container:has(div.metric-trigger-marker-2) + div.element-container button p,
    div.element-container:has(div.metric-trigger-marker-3) + div.element-container button p {
        color: #f0f2ff !important;
        margin: 0 !important;
    }
    div.element-container:has(div.metric-trigger-marker) + div.element-container button strong,
    div.element-container:has(div.metric-trigger-marker-2) + div.element-container button strong,
    div.element-container:has(div.metric-trigger-marker-3) + div.element-container button strong {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.3em !important;
        color: #f0f2ff !important;
    }

    /* --- Kafelki przełączające widok główny: Analiza / Złoto / Zagrożenia --- */
    div.element-container:has(div.view-trigger-marker-a) + div.element-container button,
    div.element-container:has(div.view-trigger-marker-b) + div.element-container button,
    div.element-container:has(div.view-trigger-marker-c) + div.element-container button {
        border-radius: 14px !important;
        padding: 16px 20px !important;
        width: 100% !important;
        backdrop-filter: blur(20px);
        transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease !important;
        box-shadow: none !important;
        text-align: center !important;
        font-weight: 600 !important;
        color: #f0f2ff !important;
    }
    /* Analiza AI - niebiesko-indygo */
    div.element-container:has(div.view-trigger-marker-a) + div.element-container button {
        background: rgba(99,102,241,0.14) !important;
        border: 1px solid rgba(99,102,241,0.28) !important;
    }
    div.element-container:has(div.view-trigger-marker-a) + div.element-container button:hover {
        transform: translateY(-2px);
        border-color: rgba(99,102,241,0.5) !important;
        background: rgba(99,102,241,0.2) !important;
    }
    /* Mapa Złota - złoty/bursztynowy */
    div.element-container:has(div.view-trigger-marker-b) + div.element-container button {
        background: rgba(234,179,8,0.14) !important;
        border: 1px solid rgba(234,179,8,0.28) !important;
    }
    div.element-container:has(div.view-trigger-marker-b) + div.element-container button:hover {
        transform: translateY(-2px);
        border-color: rgba(234,179,8,0.5) !important;
        background: rgba(234,179,8,0.2) !important;
    }
    /* Monitor Zagrożeń - czerwony */
    div.element-container:has(div.view-trigger-marker-c) + div.element-container button {
        background: rgba(239,68,68,0.14) !important;
        border: 1px solid rgba(239,68,68,0.28) !important;
    }
    div.element-container:has(div.view-trigger-marker-c) + div.element-container button:hover {
        transform: translateY(-2px);
        border-color: rgba(239,68,68,0.5) !important;
        background: rgba(239,68,68,0.2) !important;
    }

    /* --- Przycisk "Powrót" - neutralny styl, bez fioletowego gradientu/blysku --- */
    div.element-container:has(div.back-btn-marker) + div.element-container button {
        background: rgba(255,255,255,0.06) !important;
        color: #c7cde3 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        font-weight: 500 !important;
        padding: 8px 18px !important;
        transition: background 0.2s ease, border-color 0.2s ease !important;
    }
    div.element-container:has(div.back-btn-marker) + div.element-container button:hover {
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.22) !important;
        color: #f0f2ff !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* --- Karty pojedynczych państw na stronie listy --- */
    .country-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 18px 16px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 16px;
        height: 100%;
    }
    .country-card:hover {
        transform: translateY(-3px);
        border-color: rgba(139,92,246,0.4);
    }
    .country-flag-icon {
        width: 56px;
        height: 40px;
        object-fit: cover;
        border-radius: 6px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.12);
    }
    .country-name {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 0.95em;
        color: #f0f2ff;
    }

    /* --- Karty pojedynczych surowców na stronie listy (zielony akcent) --- */
    .commodity-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 24px 16px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 16px;
        height: 100%;
    }
    .commodity-card:hover {
        transform: translateY(-3px);
        border-color: rgba(34,197,94,0.45);
    }
    .commodity-icon {
        font-size: 2.0em;
        margin-bottom: 8px;
    }
    .commodity-name {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 0.95em;
        color: #f0f2ff;
    }

    /* --- Karty kategorii zagrożeń (kolor per kategoria + liczba państw) --- */
    .threat-card {
        border-radius: 16px;
        padding: 28px 20px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 16px;
        height: 100%;
    }
    .threat-card:hover {
        transform: translateY(-3px);
    }
    .threat-icon {
        font-size: 2.2em;
        margin-bottom: 10px;
    }
    .threat-name {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.1em;
        color: #f0f2ff;
        margin-bottom: 4px;
    }
    .threat-count {
        font-size: 0.82em;
        color: #c7cde3;
    }

    /* --- Metric cards row --- */
    .metric-card {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 16px;
        padding: 18px 20px;
        text-align: center;
        backdrop-filter: blur(20px);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(139,92,246,0.4);
    }
    .metric-icon {
        font-size: 1.6em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.3em;
        color: #f0f2ff;
    }
    .metric-label {
        color: #7b83a8;
        font-size: 0.78em;
        margin-top: 2px;
    }

    /* --- Footer --- */
    .footer-text {
        text-align: center;
        font-size: 0.82em;
        color: #5a6188;
        padding: 20px 0 10px 0;
    }
    .footer-text b {
        color: #7b83a8;
    }

    /* --- Chart container --- */
    .chart-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 6px;
    }

    /* --- Divider ładniejszy --- */
    hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 22px 0 !important;
    }

    /* --- Error / spinner text --- */
    .stSpinner > div {
        color: #a7afd1 !important;
    }

    /* --- selectbox label --- */
    .stSelectbox label, .stRadio label, .stTextInput label {
        color: #c7cde3 !important;
        font-weight: 500 !important;
        font-size: 0.92em !important;
    }

    /* --- Expander w sidebarze (Zaawansowane ustawienia) --- */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
    }
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        color: #e4e7f7 !important;
        font-weight: 600 !important;
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
    'Country': [
        'Ukraina', 'Rosja', 'Izrael', 'Palestyna', 'Syria', 'Jemen', 'Tajwan', 'Korea Północna', 'Iran', 
        'Afganistan', 'Somalia', 'Mali', 'Burkina Faso', 'Niger', 'DR Konga', 'Wenezuela', 'Argentyna', 
        'Turcja', 'Egipt', 'Pakistan', 'Liban', 'Meksyk', 'Mjanma', 'Irak', 'Gruzja', 'Nigeria', 'Kuba'
    ],
    'ISO_Code': [
        'UKR', 'RUS', 'ISR', 'PSE', 'SYR', 'YEM', 'TWN', 'PRK', 'IRN', 
        'AFG', 'SOM', 'MLI', 'BFA', 'NER', 'COD', 'VEN', 'ARG', 
        'TUR', 'EGY', 'PAK', 'LBN', 'MEX', 'MMR', 'IRQ', 'GEO', 'NGA', 'CUB'
    ],
    'Kategoria': [
        'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Wojna', 'Niestabilność Polityczna', 'Niestabilność Polityczna', 'Niestabilność Polityczna', 
        'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Terroryzm', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 
        'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Kryzys Gospodarczy', 'Konflikt zbrojny', 'Konflikt zbrojny', 
        'Niestabilność Polityczna', 'Niestabilność Polityczna', 'Terroryzm', 'Kryzys Gospodarczy'
    ]
}
df_threats = pd.DataFrame(threat_data)

color_map_threats = {
    'Wojna': '#ef4444',
    'Konflikt zbrojny': '#dc2626',
    'Niestabilność Polityczna': '#f97316',
    'Terroryzm': '#ea580c',
    'Kryzys Gospodarczy': '#a855f7'
}

ALL_COUNTRIES = sorted([
    "Afganistan", "Albania", "Algieria", "Andora", "Angola", "Antigua i Barbuda", "Arabia Saudyjska", "Argentyna", "Armenia",
    "Australia", "Austria", "Azerbejdżan", "Bahamy", "Bahrajn", "Bangladesz", "Barbados", "Belgia", "Belize", "Benin", "Bhutan",
    "Białoruś", "Boliwia", "Bośnia i Hercegowina", "Botswana", "Brazylia", "Brunei", "Bułgaria", "Burkina Faso", "Burundi",
    "Chile", "Chiny", "Chorwacja", "Cypr", "Czad", "Czarnogóra", "Czechy", "Dania", "Demokratyczna Republika Konga", "Dominika",
    "Dominikana", "Dżibuti", "Egipt", "Ekwador", "Erytrea", "Estonia", "Eswatini", "Etiopia", "Fidżi", "Filipiny", "Finlandia",
    "Francja", "Gabon", "Gambia", "Ghana", "Grecja", "Grenada", "Gruzja", "Gujana", "Gwatemala", "Gwinea", "Gwinea Bissau",
    "Gwinea Równikowa", "Haiti", "Hiszpania", "Holandia", "Honduras", "Indie", "Indonezja", "Irak", "Iran", "Irlandia",
    "Islandia", "Izrael", "Jamajka", "Japonia", "Jemen", "Jordania", "Kambodża", "Kamerun", "Kanada", "Katar", "Kazachstan",
    "Kenia", "Kirgistan", "Kiribati", "Kolumbia", "Komory", "Kongo", "Korea Południowa", "Korea Północna", "Kostaryka", "Kuba",
    "Kuwejt", "Laos", "Lesotho", "Liban", "Liberia", "Libia", "Liechtenstein", "Litwa", "Luksemburg", "Łotwa",
    "Macedonia Północna", "Madagaskar", "Malawi", "Malediwy", "Malezja", "Mali", "Malta", "Maroko", "Mauretania", "Mauritius",
    "Meksyk", "Mikronezja", "Mołdawia", "Monako", "Mongolia", "Mozambik", "Namibia", "Nauru", "Nepal", "Niemcy", "Niger",
    "Nigeria", "Nikaragua", "Norwegia", "Nowa Zelandia", "Oman", "Pakistan", "Palau", "Palestyna", "Panama",
    "Papua-Nowa Gwinea", "Paragwaj", "Peru", "Polska", "Portugalia", "Republika Południowej Afryki",
    "Republika Środkowoafrykańska", "Republika Zielonego Przylądka", "Rosja", "Rumunia", "Rwanda", "Saint Kitts i Nevis",
    "Saint Lucia", "Saint Vincent i Grenadyny", "Salwador", "Samoa", "San Marino", "Senegal", "Serbia", "Seszele",
    "Sierra Leone", "Singapur", "Słowacja", "Słowenia", "Somalia", "Sri Lanka", "Sudan", "Sudan Południowy", "Surinam",
    "Syria", "Szwajcaria", "Szwecja", "Tadżykistan", "Tajlandia", "Tajwan", "Tanzania", "Timor Wschodni", "Togo", "Tonga",
    "Trynidad i Tobago", "Tunezja", "Turcja", "Turkmenistan", "Tuvalu", "Uganda", "Ukraina", "Urugwaj", "USA", "Uzbekistan",
    "Vanuatu", "Watykan", "Wenezuela", "Węgry", "Wielka Brytania", "Wietnam", "Włochy", "Wybrzeże Kości Słoniowej",
    "Wyspy Marshalla", "Wyspy Salomona", "Wyspy Świętego Tomasza i Książęca", "Zambia", "Zimbabwe", "ZEA"
])

COMMODITIES = sorted(["Gaz Ziemny", "Ropa Naftowa", "Węgiel Kamienny", "Uran", "Wodór", "Miedź", "Aluminium", "Żelazo", "Nikiel", "Cynk", "Złoto", "Srebro", "Platyna", "Lit", "Kobalt", "Metale Ziem Rzadkich", "Grafit", "Krzem", "Magnez", "Pszenica (Zboże)", "Kukurydza", "Rzepak", "Ryż", "Kawa", "Kauczuk"])

# --- 3b. Mapowanie Państwo -> Kod ISO (do generowania flag) ---
COUNTRY_ISO_MAP = {
    "Afganistan": "AF", "Albania": "AL", "Algieria": "DZ", "Andora": "AD", "Angola": "AO",
    "Antigua i Barbuda": "AG", "Arabia Saudyjska": "SA", "Argentyna": "AR", "Armenia": "AM",
    "Australia": "AU", "Austria": "AT", "Azerbejdżan": "AZ", "Bahamy": "BS", "Bahrajn": "BH",
    "Bangladesz": "BD", "Barbados": "BB", "Belgia": "BE", "Belize": "BZ", "Benin": "BJ",
    "Bhutan": "BT", "Białoruś": "BY", "Boliwia": "BO", "Bośnia i Hercegowina": "BA",
    "Botswana": "BW", "Brazylia": "BR", "Brunei": "BN", "Bułgaria": "BG", "Burkina Faso": "BF",
    "Burundi": "BI", "Chile": "CL", "Chiny": "CN", "Chorwacja": "HR", "Cypr": "CY", "Czad": "TD",
    "Czarnogóra": "ME", "Czechy": "CZ", "Dania": "DK", "Demokratyczna Republika Konga": "CD",
    "Dominika": "DM", "Dominikana": "DO", "Dżibuti": "DJ", "Egipt": "EG", "Ekwador": "EC",
    "Erytrea": "ER", "Estonia": "EE", "Eswatini": "SZ", "Etiopia": "ET", "Fidżi": "FJ",
    "Filipiny": "PH", "Finlandia": "FI", "Francja": "FR", "Gabon": "GA", "Gambia": "GM",
    "Ghana": "GH", "Grecja": "GR", "Grenada": "GD", "Gruzja": "GE", "Gujana": "GY",
    "Gwatemala": "GT", "Gwinea": "GN", "Gwinea Bissau": "GW", "Gwinea Równikowa": "GQ",
    "Haiti": "HT", "Hiszpania": "ES", "Holandia": "NL", "Honduras": "HN", "Indie": "IN",
    "Indonezja": "ID", "Irak": "IQ", "Iran": "IR", "Irlandia": "IE", "Islandia": "IS",
    "Izrael": "IL", "Jamajka": "JM", "Japonia": "JP", "Jemen": "YE", "Jordania": "JO",
    "Kambodża": "KH", "Kamerun": "CM", "Kanada": "CA", "Katar": "QA", "Kazachstan": "KZ",
    "Kenia": "KE", "Kirgistan": "KG", "Kiribati": "KI", "Kolumbia": "CO", "Komory": "KM",
    "Kongo": "CG", "Korea Południowa": "KR", "Korea Północna": "KP", "Kostaryka": "CR",
    "Kuba": "CU", "Kuwejt": "KW", "Laos": "LA", "Lesotho": "LS", "Liban": "LB",
    "Liberia": "LR", "Libia": "LY", "Liechtenstein": "LI", "Litwa": "LT", "Luksemburg": "LU",
    "Łotwa": "LV", "Macedonia Północna": "MK", "Madagaskar": "MG", "Malawi": "MW",
    "Malediwy": "MV", "Malezja": "MY", "Mali": "ML", "Malta": "MT", "Maroko": "MA",
    "Mauretania": "MR", "Mauritius": "MU", "Meksyk": "MX", "Mikronezja": "FM",
    "Mołdawia": "MD", "Monako": "MC", "Mongolia": "MN", "Mozambik": "MZ", "Namibia": "NA",
    "Nauru": "NR", "Nepal": "NP", "Niemcy": "DE", "Niger": "NE", "Nigeria": "NG",
    "Nikaragua": "NI", "Norwegia": "NO", "Nowa Zelandia": "NZ", "Oman": "OM",
    "Pakistan": "PK", "Palau": "PW", "Palestyna": "PS", "Panama": "PA",
    "Papua-Nowa Gwinea": "PG", "Paragwaj": "PY", "Peru": "PE", "Polska": "PL",
    "Portugalia": "PT", "Republika Południowej Afryki": "ZA",
    "Republika Środkowoafrykańska": "CF", "Republika Zielonego Przylądka": "CV",
    "Rosja": "RU", "Rumunia": "RO", "Rwanda": "RW", "Saint Kitts i Nevis": "KN",
    "Saint Lucia": "LC", "Saint Vincent i Grenadyny": "VC", "Salwador": "SV",
    "Samoa": "WS", "San Marino": "SM", "Senegal": "SN", "Serbia": "RS", "Seszele": "SC",
    "Sierra Leone": "SL", "Singapur": "SG", "Słowacja": "SK", "Słowenia": "SI",
    "Somalia": "SO", "Sri Lanka": "LK", "Sudan": "SD", "Sudan Południowy": "SS",
    "Surinam": "SR", "Syria": "SY", "Szwajcaria": "CH", "Szwecja": "SE",
    "Tadżykistan": "TJ", "Tajlandia": "TH", "Tajwan": "TW", "Tanzania": "TZ",
    "Timor Wschodni": "TL", "Togo": "TG", "Tonga": "TO", "Trynidad i Tobago": "TT",
    "Tunezja": "TN", "Turcja": "TR", "Turkmenistan": "TM", "Tuvalu": "TV",
    "Uganda": "UG", "Ukraina": "UA", "Urugwaj": "UY", "USA": "US", "Uzbekistan": "UZ",
    "Vanuatu": "VU", "Watykan": "VA", "Wenezuela": "VE", "Węgry": "HU",
    "Wielka Brytania": "GB", "Wietnam": "VN", "Włochy": "IT",
    "Wybrzeże Kości Słoniowej": "CI", "Wyspy Marshalla": "MH", "Wyspy Salomona": "SB",
    "Wyspy Świętego Tomasza i Książęca": "ST", "Zambia": "ZM", "Zimbabwe": "ZW", "ZEA": "AE"
}

def country_flag_url(country_name, width=80):
    """Zwraca URL do prawdziwego obrazu flagi (PNG) z darmowego CDN flagcdn.com,
    na podstawie kodu ISO alpha-2 kraju. Renderuje się poprawnie na każdym systemie
    (w przeciwieństwie do emoji flag, których Windows nie wyświetla)."""
    iso = COUNTRY_ISO_MAP.get(country_name)
    if not iso:
        return None
    return f"https://flagcdn.com/w{width}/{iso.lower()}.png"

# --- 4. Języki ---
LANG = {
    "Polska 🇵🇱": {
        "code": "PL", "slogan": "Strategiczna Analityka wspierana przez AI",
        "api_label": "Klucz API OpenAI", "nav_analysis": "Analiza Tekstowa",
        "nav_maps": "Moduł Wizualny", "mode_label": "Wybierz tryb:",
        "mode_res": "💎 Surowce Strategiczne", "mode_pol": "🏛️ Polityka", "mode_rel": "🤝 Analiza Relacji",
        "map_option_off": "Wyłączony", "map_option_gold": "Mapa Rezerw Złota", "map_option_threats": "Globalny Monitor Zagrożeń",
        "country_label": "Wybierz Państwo:", "country2_label": "Wybierz drugie Państwo:",
        "res_label": "Wybierz Surowiec:", "pol_submode_label": "Obszar polityki:",
        "pol_options": ["Partie Polityczne", "System Władzy", "Główne Osoby w Państwie"],
        "btn_gen": "🚀 GENERUJ RAPORT", "status_wait": "Oczekiwanie na instrukcje",
        "status_work": "Generowanie raportu...", "loading": "Trwa analiza...",
        "footer": "Projekt edukacyjny - Uniwersytet Warszawski",
        "score_label": "Wskaźnik Bezpieczeństwa Strategicznego (1-10):",
        "config_title": "Konfiguracja", "config_sub": "Ustaw parametry analizy",
        "select_title": "Parametry Analizy", "select_sub": "Wybierz państwo oraz przedmiot analizy",
        "m1_label": "Państwa w bazie", "m2_label": "Surowce", "m3_label": "Zagrożenia globalne", "m4_label": "Model AI",
        "back_label": "← Powrót", "countries_page_title": "Wszystkie państwa w bazie",
        "commodities_page_title": "Wszystkie surowce w bazie",
        "threats_page_title": "Kategorie globalnych zagrożeń",
        "threat_country_count": "państw",
        "reset_label": "🔄 Reset"
    },
    "English 🇬🇧": {
        "code": "EN", "slogan": "AI-Powered Strategic Intelligence",
        "api_label": "OpenAI API Key", "nav_analysis": "Textual Analysis",
        "nav_maps": "Visual Module", "mode_label": "Select mode:",
        "mode_res": "💎 Strategic Commodities", "mode_pol": "🏛️ Politics", "mode_rel": "🤝 Relationship Analysis",
        "map_option_off": "Disabled", "map_option_gold": "Gold Reserves Map", "map_option_threats": "Global Threat Monitor",
        "country_label": "Select Country:", "country2_label": "Select second Country:",
        "res_label": "Select Commodity:", "pol_submode_label": "Politics area:",
        "pol_options": ["Political Parties", "Government System", "Key Figures"],
        "btn_gen": "🚀 GENERATE REPORT", "status_wait": "Ready & Waiting",
        "status_work": "Generating report...", "loading": "Analyzing...",
        "footer": "Educational Project - University of Warsaw",
        "score_label": "Strategic Security Score (1-10):",
        "config_title": "Configuration", "config_sub": "Set analysis parameters",
        "select_title": "Analysis Parameters", "select_sub": "Choose country and analysis target",
        "m1_label": "Countries in DB", "m2_label": "Commodities", "m3_label": "Global threats", "m4_label": "AI Model",
        "back_label": "← Back", "countries_page_title": "All countries in database",
        "commodities_page_title": "All commodities in database",
        "threats_page_title": "Global threat categories",
        "threat_country_count": "countries",
        "reset_label": "🔄 Reset"
    }
}

# --- 5. Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">🌍 GeoCommodity</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Insights Terminal v2.0</div>', unsafe_allow_html=True)

    lang_display = st.selectbox("🌐 Language / Język", list(LANG.keys()))
    L = LANG[lang_display]
    st.markdown("---")

    st.markdown(f'<div class="sidebar-title" style="font-size:0.95em;">📂 {L["nav_analysis"]}</div>', unsafe_allow_html=True)
    analysis_mode = st.radio(L["mode_label"], [L["mode_res"], L["mode_pol"], L["mode_rel"]], label_visibility="collapsed")
    st.markdown("---")

    with st.expander(f"⚙️ {L['config_title']}", expanded=True):
        st.markdown(f'<div class="sidebar-sub" style="margin-top:-8px;">{L["config_sub"]}</div>', unsafe_allow_html=True)
        model_version = st.selectbox("🤖 Model AI:", ["gpt-4o-mini", "gpt-4o"])
        api_key = st.text_input(f"🔑 {L['api_label']}", type="password")

# --- 6. Logo / Hero Header ---
def get_transparent_logo_base64(file_path):
    """Wczytuje logo i usuwa białe/jasne tło, zwracając obraz PNG (RGBA) jako base64."""
    from PIL import Image
    import numpy as np
    from io import BytesIO

    img = Image.open(file_path).convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Piksele czysto białe -> w pełni przezroczyste
    white_mask = (r > 235) & (g > 235) & (b > 235)
    data[:, :, 3] = np.where(white_mask, 0, 255)

    # Piksele prawie białe (antyaliasing na krawędziach liter) -> częściowa przezroczystość
    near_white = (r > 200) & (g > 200) & (b > 200) & ~white_mask
    avg = (r.astype(int) + g.astype(int) + b.astype(int)) / 3
    alpha_partial = np.clip((255 - avg) / (255 - 200) * 255, 0, 255).astype(np.uint8)
    data[:, :, 3] = np.where(near_white, alpha_partial, data[:, :, 3])

    result = Image.fromarray(data, "RGBA")
    buffer = BytesIO()
    result.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

if os.path.exists("logo.png"):
    encoded_logo = get_transparent_logo_base64("logo.png")
    st.markdown(f'''
        <div style="display: flex; justify-content: center; align-items: center; padding-top: 15px; background: transparent;">
            <img src="data:image/png;base64,{encoded_logo}" width="420" style="background: transparent; filter: drop-shadow(0 4px 20px rgba(139,92,246,0.25));">
        </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="brand-title">🌍 GeoCommodity Insights</div>
        <div class="brand-slogan">{L['slogan']}</div>
    </div>
    """, unsafe_allow_html=True)

status_placeholder = st.empty()
status_placeholder.markdown(f'''
    <div class="status-container">
        <div class="status-pill">
            <span class="status-dot"></span>
            {L["slogan"]} · <span class="status-highlight">{L["status_wait"]}</span>
        </div>
    </div>
''', unsafe_allow_html=True)

# --- Inicjalizacja stanu nawigacji ---
if "show_countries_page" not in st.session_state:
    st.session_state.show_countries_page = False
if "show_commodities_page" not in st.session_state:
    st.session_state.show_commodities_page = False
if "show_threats_page" not in st.session_state:
    st.session_state.show_threats_page = False

# --- 6b. Metric cards ---
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
with mcol1:
    st.markdown('<div class="metric-trigger-marker"></div>', unsafe_allow_html=True)
    if st.button(f"🌐\n\n**{len(ALL_COUNTRIES)}**\n\n{L['m1_label']}", key="countries_trigger_btn", use_container_width=True):
        st.session_state.show_countries_page = True
        st.session_state.show_commodities_page = False
        st.session_state.show_threats_page = False
        st.rerun()
with mcol2:
    st.markdown('<div class="metric-trigger-marker-2"></div>', unsafe_allow_html=True)
    if st.button(f"💎\n\n**{len(COMMODITIES)}**\n\n{L['m2_label']}", key="commodities_trigger_btn", use_container_width=True):
        st.session_state.show_commodities_page = True
        st.session_state.show_countries_page = False
        st.session_state.show_threats_page = False
        st.rerun()
with mcol3:
    st.markdown('<div class="metric-trigger-marker-3"></div>', unsafe_allow_html=True)
    if st.button(f"⚠️\n\n**{len(df_threats)}**\n\n{L['m3_label']}", key="threats_trigger_btn", use_container_width=True):
        st.session_state.show_threats_page = True
        st.session_state.show_countries_page = False
        st.session_state.show_commodities_page = False
        st.rerun()
with mcol4:
    st.markdown(f'''<div class="metric-card"><div class="metric-icon">🤖</div>
        <div class="metric-value" style="font-size:0.95em;">{model_version}</div>
        <div class="metric-label">{L["m4_label"]}</div></div>''', unsafe_allow_html=True)

st.markdown("---")

# --- 7. Interfejs Główny ---
if st.session_state.show_countries_page:
    st.markdown('<div class="back-btn-marker"></div>', unsafe_allow_html=True)
    if st.button(L["back_label"], key="back_btn"):
        st.session_state.show_countries_page = False
        st.rerun()

    st.markdown(f'<h3 style="color:#f0f2ff; text-align:center; margin-top:10px;">🌍 {L["countries_page_title"]} ({len(ALL_COUNTRIES)})</h3>', unsafe_allow_html=True)
    st.write("")

    country_cols = st.columns(4)
    for idx, country in enumerate(ALL_COUNTRIES):
        flag_url = country_flag_url(country, width=80)
        with country_cols[idx % 4]:
            st.markdown(f'''<div class="country-card">
                <img class="country-flag-icon" src="{flag_url}" alt="{country}" loading="lazy">
                <div class="country-name">{country}</div>
            </div>''', unsafe_allow_html=True)

elif st.session_state.show_commodities_page:
    st.markdown('<div class="back-btn-marker"></div>', unsafe_allow_html=True)
    if st.button(L["back_label"], key="back_btn_commodities"):
        st.session_state.show_commodities_page = False
        st.rerun()

    st.markdown(f'<h3 style="color:#f0f2ff; text-align:center; margin-top:10px;">💎 {L["commodities_page_title"]} ({len(COMMODITIES)})</h3>', unsafe_allow_html=True)
    st.write("")

    commodity_cols = st.columns(4)
    for idx, commodity in enumerate(COMMODITIES):
        with commodity_cols[idx % 4]:
            st.markdown(f'''<div class="commodity-card">
                <div class="commodity-icon">💎</div>
                <div class="commodity-name">{commodity}</div>
            </div>''', unsafe_allow_html=True)

elif st.session_state.show_threats_page:
    st.markdown('<div class="back-btn-marker"></div>', unsafe_allow_html=True)
    if st.button(L["back_label"], key="back_btn_threats"):
        st.session_state.show_threats_page = False
        st.rerun()

    st.markdown(f'<h3 style="color:#f0f2ff; text-align:center; margin-top:10px;">⚠️ {L["threats_page_title"]}</h3>', unsafe_allow_html=True)
    st.write("")

    threat_category_order = ["Wojna", "Konflikt zbrojny", "Niestabilność Polityczna", "Terroryzm", "Kryzys Gospodarczy"]
    threat_icons = {
        "Wojna": "⚔️",
        "Konflikt zbrojny": "💥",
        "Niestabilność Polityczna": "🏛️",
        "Terroryzm": "💣",
        "Kryzys Gospodarczy": "📉"
    }

    threat_cols = st.columns(len(threat_category_order))
    for idx, category in enumerate(threat_category_order):
        color_hex = color_map_threats.get(category, "#e74c3c")
        count = int((df_threats["Kategoria"] == category).sum())
        icon = threat_icons.get(category, "⚠️")
        with threat_cols[idx]:
            st.markdown(f'''<div class="threat-card" style="background: {color_hex}26; border: 1px solid {color_hex}66;">
                <div class="threat-icon">{icon}</div>
                <div class="threat-name">{category}</div>
                <div class="threat-count">{count} {L["threat_country_count"]}</div>
            </div>''', unsafe_allow_html=True)

else:
    # --- Inicjalizacja aktywnego widoku (domyślnie: Analiza AI) ---
    if "active_view" not in st.session_state:
        st.session_state.active_view = "analysis"

    dot_a = "🔵" if st.session_state.active_view == "analysis" else "⚪"
    dot_b = "🔵" if st.session_state.active_view == "gold" else "⚪"
    dot_c = "🔵" if st.session_state.active_view == "threats" else "⚪"

    vcol1, vcol2, vcol3 = st.columns(3)
    with vcol1:
        st.markdown('<div class="view-trigger-marker-a"></div>', unsafe_allow_html=True)
        if st.button(f"{dot_a}  📊  {L['nav_analysis']}", key="view_analysis_btn", use_container_width=True):
            st.session_state.active_view = "analysis"
            st.rerun()
    with vcol2:
        st.markdown('<div class="view-trigger-marker-b"></div>', unsafe_allow_html=True)
        if st.button(f"{dot_b}  🥇  {L['map_option_gold']}", key="view_gold_btn", use_container_width=True):
            st.session_state.active_view = "gold"
            st.rerun()
    with vcol3:
        st.markdown('<div class="view-trigger-marker-c"></div>', unsafe_allow_html=True)
        if st.button(f"{dot_c}  🚨  {L['map_option_threats']}", key="view_threats_btn", use_container_width=True):
            st.session_state.active_view = "threats"
            st.rerun()

    st.write("")

    if st.session_state.active_view == "gold":
        st.markdown(f'<div class="chart-header"><h3 style="color:#f0f2ff;">🥇 {L["map_option_gold"]}</h3></div>', unsafe_allow_html=True)
        fig = px.choropleth(df_gold, locations="ISO_Code", color="Log_Tons", hover_name="Country",
                            hover_data={"Log_Tons": False, "Tons": True},
                            color_continuous_scale="Spectral_r", labels={'Log_Tons':'Skala Potęgi', 'Tons': 'Tony'})
        fig.update_layout(
            geo=dict(showframe=False, projection_type='natural earth', bgcolor='rgba(0,0,0,0)',
                     landcolor='rgba(255,255,255,0.03)', showland=True,
                     subunitcolor='rgba(255,255,255,0.1)'),
            margin={"r":0,"t":20,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c7cde3'
        )
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.active_view == "threats":
        st.markdown(f'<div class="chart-header"><h3 style="color:#f0f2ff;">🚨 {L["map_option_threats"]}</h3></div>', unsafe_allow_html=True)
        fig_threats = px.choropleth(df_threats, locations="ISO_Code", color="Kategoria", hover_name="Country",
                            color_discrete_map=color_map_threats, 
                            category_orders={"Kategoria": ["Wojna", "Konflikt zbrojny", "Niestabilność Polityczna", "Terroryzm", "Kryzys Gospodarczy"]},
                            labels={'Kategoria':''})
        fig_threats.update_layout(
            geo=dict(showframe=False, projection_type='natural earth', bgcolor='rgba(0,0,0,0)',
                     landcolor='rgba(255,255,255,0.03)', showland=True,
                     subunitcolor='rgba(255,255,255,0.1)'),
            margin={"r":0,"t":20,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c7cde3',
            legend=dict(bgcolor='rgba(255,255,255,0.05)', bordercolor='rgba(255,255,255,0.1)', borderwidth=1)
        )
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_threats, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown(f'''
            <div class="glass-card-title">🎯 {L["select_title"]}</div>
            <div class="glass-card-sub">{L["select_sub"]}</div>
        ''', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1: selected_country = st.selectbox(f"📍 {L['country_label']}", ALL_COUNTRIES, key="sel_country")
        with col2:
            if analysis_mode == L["mode_res"]: target_item = st.selectbox(f"💎 {L['res_label']}", COMMODITIES, key="sel_target")
            elif analysis_mode == L["mode_pol"]: target_item = st.selectbox(f"🔍 {L['pol_submode_label']}", L["pol_options"], key="sel_target")
            else: target_item = st.selectbox(f"🤝 {L['country2_label']}", ALL_COUNTRIES, index=1, key="sel_target")

        st.write("")

        if "last_report" not in st.session_state:
            st.session_state.last_report = None

        # Przycisk Reset pojawia się dopiero, gdy istnieje wygenerowany raport
        if st.session_state.last_report is not None:
            gen_col, reset_col = st.columns([4, 1])
        else:
            gen_col = st.container()
            reset_col = None

        with gen_col:
            generate_clicked = st.button(L["btn_gen"], use_container_width=True)

        if reset_col is not None:
            with reset_col:
                st.markdown('<div class="back-btn-marker"></div>', unsafe_allow_html=True)
                if st.button(L["reset_label"], key="reset_btn", use_container_width=True):
                    for k in ["sel_country", "sel_target"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.session_state.last_report = None
                    st.rerun()

        if generate_clicked:
            if not api_key: 
                st.error("⚠️ Podaj klucz API!")
            else:
                try:
                    status_placeholder.markdown(f'''
                        <div class="status-container">
                            <div class="status-pill">
                                <span class="status-dot working"></span>
                                {L["slogan"]} · <span class="status-highlight" style="color: #fbbf24;">{L["status_work"]}</span>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                    client = OpenAI(api_key=api_key)
                    with st.spinner(L["loading"]):
                        clean_mode_label = re.sub(r'^[^\w]+', '', analysis_mode).strip()
                        prompt = f"Analiza {target_item} w {selected_country}. {clean_mode_label}. Nie używaj żadnych hasztagów (#). Nagłówki sekcji zapisuj jako pogrubiony tekst zakończony dwukropkiem (np. **Tytuł sekcji:**). Na samym końcu napisz tylko: SCORE: X (gdzie X to liczba 1-10)."
                        resp = client.chat.completions.create(model=model_version,
                            messages=[{"role": "system", "content": f"Ekspert geopolityki. Język: {L['code']}."},
                                      {"role": "user", "content": prompt}])
                        full_response = resp.choices[0].message.content
                        processed_text = re.sub(r'^#+\s*(.*)', r'**\1:**', full_response, flags=re.MULTILINE)
                        score_match = re.search(r"SCORE:\s*(\d+)", processed_text)
                        clean_report = re.sub(r"SCORE:\s*\d+", "", processed_text)

                        st.session_state.last_report = {
                            "country": selected_country,
                            "target": target_item,
                            "text": clean_report,
                            "score": int(score_match.group(1)) if score_match else None,
                        }
                    status_placeholder.markdown(f'''
                        <div class="status-container">
                            <div class="status-pill">
                                <span class="status-dot"></span>
                                {L["slogan"]} · <span class="status-highlight">{L["status_wait"]}</span>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                    st.rerun()
                except Exception as e: 
                    st.error(f"❌ Błąd: {e}")

        # --- Renderowanie zapamiętanego raportu (widoczny dopóki nie klikniesz Reset) ---
        if st.session_state.last_report is not None:
            report = st.session_state.last_report
            if report["score"] is not None:
                score_val = report["score"]
                if score_val >= 9: color_hex = "#4ade80"; status_txt = "Optymalny"; status_icon = "✅"
                elif score_val >= 7: color_hex = "#60a5fa"; status_txt = "Stabilny"; status_icon = "🔵"
                elif score_val >= 4: color_hex = "#fbbf24"; status_txt = "Umiarkowane ryzyko"; status_icon = "🟡"
                else: color_hex = "#f87171"; status_txt = "Wysokie ryzyko"; status_icon = "🔴"

                st.markdown(f'<style>div[data-testid="stProgress"] > div > div > div > div {{ background: {color_hex} !important; box-shadow: 0 0 12px {color_hex}80; }}</style>', unsafe_allow_html=True)
                st.markdown('<div class="score-badge-wrap">', unsafe_allow_html=True)
                st.markdown(f'<div class="score-title">{L["score_label"]}</div>', unsafe_allow_html=True)
                st.progress(score_val / 10)
                st.markdown(f'<p class="score-status-text" style="color:{color_hex};">{status_icon} {status_txt} — {score_val}/10</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="report-card"><h3>📄 {report["country"]} · {report["target"]}</h3>{report["text"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<div class='footer-text'>© 2026 <b>GeoCommodity Insights</b> · {L['footer']}</div>", unsafe_allow_html=True)
