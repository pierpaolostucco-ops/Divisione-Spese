import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configurazione pagina
st.set_page_config(page_title="Divisione Spese", page_icon="⚖️", layout="wide")

# --- CONNESSIONE GOOGLE SHEETS ---
url = "IL_TUO_URL_DI_GOOGLE_SHEETS" 
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("⚖️ Divisione Spese (Pierpaolo & Martina)")
st.markdown("---")

# --- SIDEBAR: INPUT ---
with st.sidebar:
    st.header("📅 Periodo")
    sel_anno = st.selectbox("Anno", [2025, 2026, 2027, 2028], index=1, key="select_anno")
    sel_mese = st.selectbox("Mese", ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                                     "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
                            index=datetime.now().month - 1, key="select_mese")
    
    st.divider()
    st.subheader("👨 Pierpaolo")
    val_stip_p = st.number_input("Stipendio Base (€)", min_value=0.0, value=2000.0, key="input_stip_p")
    val_bonus_p = st.number_input("Bonus / Extra (€)", min_value=0.0, value=0.0, key="input_bonus_p")
    tot_p = val_stip_p + val_bonus_p

    st.subheader("👩 Martina")
    val_stip_m = st.number_input("Stipendio Base (€)", min_value=0.0, value=1500.0, key="input_stip_m")
    val_bonus_m = st.number_input("Bonus / Extra (€)", min_value=0.0, value=0.0, key="input_bonus_m")
    tot_m = val_stip_m + val_bonus_m

# --- CALCOLI ---
tot_entrate = tot_p + tot_m
if tot_entrate > 0:
    p_p = tot_p / tot_entrate
    p_m = tot_m / tot_entrate
else:
    p_p = p_m = 0.5

# --- SEZIONE SPESE ---
st.header(f"📊 Spese di {sel_mese} {sel_anno}")
col_input, col_graph = st.columns(2)

with col_input:
    val_mutuo = st.number_input("Mutuo / Affitto (€)", value=800.0, key="input_mutuo")
    val_bollette = st.number_input("Bollette (€)", value=150.0, key="input_bollette")
    val_cibo = st.number_input("Spesa (€)", value=300.0, key="input_cibo")
    val_extra = st.number_input("Altro (€)", value=50.0, key="input_extra")
    tot_spese = val_mutuo + val_bollette + val_cibo + val_extra

# --- RISULTATI ---
quota_p = tot_spese * p_p
quota_m = tot_spese * p_m
mutuo_p = val_mutuo * p_p
mutuo_m = val_mutuo * p_m

with col_graph:
    df_pie = pd.DataFrame({"Persona": ["Pierpaolo", "Martina"], "Quota": [quota_p, quota_m]})
    fig = px.pie(df_pie, values='Quota', names='Persona', 
                 color_discrete_sequence=['#1E88E5', '#D81B60'], hole=.4)
    st.plotly_chart(fig, use_container_width=True)

# --- DETTAGLIO VERSAMENTI ---
st.divider()
st.subheader("📌 Quanto versare sul conto comune")
c1, c2 = st.columns(2)

with c1:
    st.info(f"### 👨 Pierpaolo\n"
            f"**Totale da versare: {quota_p:.2f} €**\n\n"
            f"Quota per il Mutuo: **{mutuo_p:.2f} €**")

with c2:
    st.error(f"### 👩 Martina\n"
             f"**Totale da versare: {quota_m:.2f} €**\n\n"
             f"Quota per il Mutuo: **{mutuo_m:.2f} €**")

# --- BOTTONE SALVATAGGIO ---
st.divider()
if st.button("💾 Salva i dati su Google Sheets", key="btn_save"):
    nuova_riga = pd.DataFrame([{
        "Data_Salvataggio": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Anno": sel_anno,
        "Mese": sel_mese,
        "Pierpaolo_Tot": tot_p,
        "Martina_Tot": tot_m,
        "Spese_Tot": tot_spese,
        "Quota_P": quota_p,
        "Quota_M": quota_m
    }])
    
    try:
        existing_data = conn.read(spreadsheet=url, worksheet="Dati")
        updated_df = pd.concat([existing_data, nuova_riga], ignore_index=True)
        conn.update(spreadsheet=url, worksheet="Dati", data=updated_df)
        st.success(f"Dati di {sel_mese} {sel_anno} salvati con successo!")
    except Exception as e:
        st.error(f"Errore durante il salvataggio: {e}")

if st.checkbox("Mostra storico salvato", key="check_history"):
    try:
        st.dataframe(conn.read(spreadsheet=url, worksheet="Dati"))
    except:
        st.warning("Nessun dato trovato nel foglio 'Dati'.")
