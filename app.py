import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configurazione pagina
st.set_page_config(page_title="Divisione Spese", page_icon="⚖️", layout="wide")

# --- CONNESSIONE GOOGLE SHEETS ---
# Sostituisci l'URL qui sotto con quello del tuo foglio
url = "INSERISCI_QUI_IL_TUO_URL_DI_GOOGLE_SHEETS"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("⚖️ Divisione Spese (Pierpaolo & Martina)")
st.markdown("---")

# --- SIDEBAR: INPUT ---
with st.sidebar:
    st.header("📅 Periodo")
    anno = st.selectbox("Anno", [2025, 2026, 2027, 2028], index=1)
    mese = st.selectbox("Mese", ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                                 "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
                        index=datetime.now().month - 1)
    
    st.divider()
    st.subheader("👨 Pierpaolo")
    stip_p = st.number_input("Stipendio Base (€)", min_value=0.0, value=2000.0)
    bonus_p = st.number_input("Bonus / Extra (€)", min_value=0.0, value=0.0)
    tot_p = stip_p + bonus_p

    st.subheader("👩 Martina")
    stip_m = st.number_input("Stipendio Base (€)", min_value=0.0, value=1500.0)
    bonus_m = st.number_input("Bonus / Extra (€)", min_value=0.0, value=0.0)
    tot_m = stip_m + bonus_m

# --- CALCOLI ---
tot_entrate = tot_p + tot_m
p_p = tot_p / tot_entrate if tot_entrate > 0 else 0.5
p_m = tot_m / tot_entrate if tot_entrate > 0 else 0.5

# --- SEZIONE SPESE ---
st.header(f"📊 Spese di {mese} {anno}")
col_input, col_graph = st.columns(2)

with col_input:
    mutuo = st.number_input("Mutuo / Affitto (€)", value=800.0)
    bollette = st.number_input("Bollette (€)", value=150.0)
    cibo = st.number_input("Spesa (€)", value=300.0)
    extra = st.number_input("Altro (€)", value=50.0)
    tot_spese = mutuo + bollette + cibo + extra

quota_p = tot_spese * p_p
quota_m = tot_spese * p_m

with col_graph:
    df_pie = pd.DataFrame({"Persona": ["Pierpaolo", "Martina"], "Quota": [quota_p, quota_m]})
    fig = px.pie(df_pie, values='Quota', names='Persona', color_discrete_sequence=['#1E88E5', '#D81B60'], hole=.4)
    st.plotly_chart(fig)

# --- BOTTONE SALVATAGGIO ---
st.divider()
if st.button("💾 Salva i dati su Google Sheets"):
    nuova_riga = pd.DataFrame([{
        "Data_Salvataggio": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Anno": anno,
        "Mese": mese,
        "Pierpaolo_Tot": tot_p,
        "Martina_Tot": tot_m,
        "Spese_Tot": tot_spese,
        "Quota_P": quota_p,
        "Quota_M": quota_m
    }])
    
    # Legge dati esistenti e concatena
    existing_data = conn.read(spreadsheet=url, worksheet="Dati")
    updated_df = pd.concat([existing_data, nuova_riga], ignore_index=True)
    conn.update(spreadsheet=url, worksheet="Dati", data=updated_df)
    st.success(f"Dati di {mese} {anno} salvati con successo!")

# Mostra lo storico
if st.checkbox("Mostra storico salvato"):
    st.dataframe(conn.read(spreadsheet=url, worksheet="Dati"))