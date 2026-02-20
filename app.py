import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Divisione Spese Casa", page_icon="⚖️", layout="wide")

# 2. CONNESSIONE GOOGLE SHEETS
try:
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Configura l'URL nei Secrets di Streamlit!")
    st.stop()

# 3. SIDEBAR - INPUT
with st.sidebar:
    st.header("📅 Periodo")
    sel_anno = st.selectbox("Anno", [2025, 2026, 2027, 2028], index=1, key="s_anno")
    sel_mese = st.selectbox("Mese", ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                                     "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
                            index=datetime.now().month - 1, key="s_mese")
    
    st.divider()
    st.subheader("👨 Pierpaolo")
    st_p = st.number_input("Stipendio Base (€)", value=2000.0, key="val_st_p")
    bo_p = st.number_input("Bonus (€)", value=0.0, key="val_bo_p")
    tot_p = st_p + bo_p

    st.subheader("👩 Martina")
    st_m = st.number_input("Stipendio Base (€)", value=1500.0, key="val_st_m")
    bo_m = st.number_input("Bonus (€)", value=0.0, key="val_bo_m")
    tot_m = st_m + bo_m

# 4. CALCOLO PERCENTUALI
tot_entrate = tot_p + tot_m
p_p = tot_p / tot_entrate if tot_entrate > 0 else 0.5
p_m = tot_m / tot_entrate if tot_entrate > 0 else 0.5

# 5. LAYOUT PRINCIPALE
st.title("⚖️ Divisione Spese")
st.subheader(f"Resoconto {sel_mese} {sel_anno}")

col_in, col_pie = st.columns([1.2, 1])

with col_in:
    st.write("### 📝 Inserimento Spese")
    c1, c2 = st.columns(2)
    with c1:
        v_mu = st.number_input("🏠 Mutuo", value=800.0)
        v_ele = st.number_input("⚡ Elettricità", value=60.0)
        v_met = st.number_input("🔥 Metano", value=80.0)
        v_acq = st.number_input("💧 Acqua", value=30.0)
    with c2:
        v_tar = st.number_input("🗑️ TARI", value=0.0)
        v_int = st.number_input("🌐 Internet", value=30.0)
        v_cib = st.number_input("🛒 Spesa", value=300.0)
        v_ext = st.number_input("📦 Altro", value=0.0)
    
    tot_spese = v_mu + v_ele + v_met + v_acq + v_tar + v_int + v_cib + v_ext
    st.info(f"**Totale Spese Comuni: {tot_spese:.2f} €**")

q_p = tot_spese * p_p
q_m = tot_spese * p_m

with col_pie:
    st.write("### 📊 Ripartizione")
    df_pie = pd.DataFrame({"Chi": ["Pierpaolo", "Martina"], "Quota": [q_p, q_m]})
    fig_pie = px.pie(df_pie, values='Quota', names='Chi', hole=.4,
                     color_discrete_sequence=['#1f77b4', '#d62728']) # Blu e Rosso standard
    st.plotly_chart(fig_pie, width="stretch")

# 6. RIEPILOGO VERSAMENTI
st.divider()
st.write("### 🏁 Quote da versare sul conto comune")
r1, r2 = st.columns(2)

with r1:
    st.metric(label="👨 Quota Pierpaolo", value=f"{q_p:.2f} €", delta=f"{p_p:.1%} del totale")
    with st.expander("Dettaglio Pierpaolo"):
        st.write(f"Mutuo: {v_mu*p_p:.2f}€ | Cibo: {v_cib*p_p:.2f}€ | Bollette: {(v_ele+v_met+v_acq)*p_p:.2f}€")

with r2:
    st.metric(label="👩 Quota Martina", value=f"{q_m:.2f} €", delta=f"{p_m:.1%} del totale")
    with st.expander("Dettaglio Martina"):
        st.write(f"Mutuo: {v_mu*p_m:.2f}€ | Cibo: {v_cib*p_m:.2f}€ | Bollette: {(v_ele+v_met+v_acq)*p_m:.2f}€")

# 7. SALVATAGGIO
st.write("")
if st.button("💾 SALVA MESE SU GOOGLE SHEETS", use_container_width=True):
    nuova_riga = pd.DataFrame([{
        "Data": datetime.now().strftime("%d/%m/%Y"),
        "Anno": sel_anno, "Mese": sel_mese,
        "Spese_Tot": tot_spese, "Quota_P": q_p, "Quota_M": q_m
    }])
    try:
        existing = conn.read(spreadsheet=url, worksheet="Dati")
        updated = pd.concat([existing, nuova_riga], ignore_index=True)
        conn.update(spreadsheet=url, worksheet="Dati", data=updated)
        st.balloons()
        st.success
