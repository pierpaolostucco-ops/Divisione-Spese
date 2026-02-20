import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Divisione Spese", page_icon="⚖️", layout="wide")

# 2. STILE CSS "MINIMAL LIGHT"
st.markdown("""
    <style>
    /* Sfondo e font generale */
    .main { background-color: #F8F9FA; }
    
    /* Sidebar più pulita */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #EEE; }
    
    /* Arrotondamento per input e box */
    .stNumberInput div div input { border-radius: 8px !important; border: 1px solid #DDD !important; }
    
    /* Styling delle card per i risultati */
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Bottone Salva stile iOS */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #007AFF;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #0056b3; border: none; color: white; }
    
    /* Titoli */
    h1, h2, h3 { color: #1C1C1E; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNESSIONE GOOGLE SHEETS
# Sostituisci con il tuo URL o usa i Secrets
url = "IL_TUO_URL_DI_GOOGLE_SHEETS" 
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. SIDEBAR - INPUT DATI
with st.sidebar:
    st.markdown("### 📅 Periodo")
    sel_anno = st.selectbox("Anno", [2025, 2026, 2027, 2028], index=1, key="select_anno")
    sel_mese = st.selectbox("Mese", ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                                     "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
                            index=datetime.now().month - 1, key="select_mese")
    
    st.markdown("---")
    st.markdown("### 👨 Pierpaolo")
    stip_p = st.number_input("Stipendio Base", min_value=0.0, value=2000.0, key="st_p")
    bon_p = st.number_input("Bonus / Extra", min_value=0.0, value=0.0, key="bo_p")
    tot_p = stip_p + bon_p

    st.markdown("### 👩 Martina")
    stip_m = st.number_input("Stipendio Base", min_value=0.0, value=1500.0, key="st_m")
    bon_m = st.number_input("Bonus / Extra", min_value=0.0, value=0.0, key="bo_m")
    tot_m = stip_m + bon_m

# 5. LOGICA MATEMATICA
tot_entrate = tot_p + tot_m
perc_p = tot_p / tot_entrate if tot_entrate > 0 else 0.5
perc_m = tot_m / tot_entrate if tot_entrate > 0 else 0.5

# 6. LAYOUT CENTRALE
st.title("Divisione Spese")
st.markdown(f"#### Situazione di {sel_mese} {sel_anno}")

col_spese, col_grafico = st.columns([1.2, 1])

with col_spese:
    with st.container():
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.subheader("📝 Inserisci i Costi")
        c1, c2 = st.columns(2)
        with c1:
            v_mutuo = st.number_input("🏠 Mutuo / Affitto", value=800.0, key="in_mu")
            v_ele = st.number_input("⚡ Elettricità", value=60.0, key="in_el")
            v_met = st.number_input("🔥 Metano", value=80.0, key="in_me")
            v_acq = st.number_input("💧 Acqua", value=30.0, key="in_ac")
        with c2:
            v_tari = st.number_input("🗑️ TARI", value=0.0, key="in_ta")
            v_int = st.number_input("🌐 Internet", value=30.0, key="in_it")
            v_cibo = st.number_input("🛒 Spesa", value=300.0, key="in_ci")
            v_ext = st.number_input("📦 Altro", value=0.0, key="in_ex")
        
        tot_spese = v_mutuo + v_ele + v_met + v_acq + v_tari + v_int + v_cibo + v_ext
        st.markdown(f"**Totale Spese Comuni: {tot_spese:.2f} €**")
        st.markdown('</div>', unsafe_allow_html=True)

with col_grafico:
    st.subheader("📊 Ripartizione")
    df_p = pd.DataFrame({"Chi": ["Pierpaolo", "Martina"], "Quota": [tot_spese*perc_p, tot_spese*perc_m]})
    fig = px.pie(df_p, values='Quota', names='Chi', 
                 color_discrete_sequence=['#007AFF', '#FF2D55'], # Blu e Rosa Apple
                 hole=.6)
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# 7. RIEPILOGO
