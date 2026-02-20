import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Divisione Spese PRO", page_icon="📈", layout="wide")

# 2. STILE CSS "DARK PRO"
st.markdown("""
    <style>
    /* Sfondo scuro per tutta l'app */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Sidebar Dark */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Card in stile Dashboard */
    .dark-card {
        background-color: #1C2128;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #30363D;
        margin-bottom: 20px;
    }
    
    /* Input numerici adattati al dark mode */
    .stNumberInput div div input {
        background-color: #0D1117 !important;
        color: white !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }

    /* Bottone con gradiente Neon */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3);
    }
    
    /* Colori metriche */
    .metric-p { color: #58A6FF; font-size: 24px; font-weight: bold; }
    .metric-m { color: #FF7B72; font-size: 24px; font-weight: bold; }
    
    hr { border-top: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNESSIONE GOOGLE SHEETS
url = "IL_TUO_URL_DI_GOOGLE_SHEETS" 
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. SIDEBAR - INPUT STIPENDI
with st.sidebar
