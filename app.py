import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configurazione pagina
st.set_page_config(page_title="Divisione Spese", page_icon="⚖️", layout="wide")

# --- CONNESSIONE GOOGLE SHEETS ---
# Sostituisci con il tuo URL o usa i Secrets di Streamlit Cloud
url = "IL_TUO_URL_DI_GOOGLE_SHEETS" 
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("⚖️ Divisione Spese (Pierpaolo & Martina)")
st.markdown("---")

# --- SIDEBAR: INPUT STIPENDI ---
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

# --- CALCOLO PERCENTUALI ---
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
    st.subheader("📝 Inserimento Costi")
    val_mutuo = st.number_input("Mutuo / Affitto (€)", value=800.0, key="in_mutuo")
    val_ele = st.number_input("Elettricità (€)", value=60.0, key="in_ele")
    val_metano = st.number_input("Metano (€)", value=80.0, key="in_met")
    val_acqua = st.number_input("Acqua (€)", value=30.0, key="in_acq")
    val_tari = st.number_input("TARI (€)", value=0.0, key="in_tari")
    val_internet = st.number_input("Internet (€)", value=30.0, key="in_int")
    val_cibo = st.number_input("Spesa Alimentare (€)", value=300.0, key="in_cibo")
    val_extra = st.number_input("Altre Spese (€)", value=0.0, key="in_extra")
    
    tot_spese = val_mutuo + val_ele + val_metano + val_acqua + val_tari + val_internet + val_cibo + val_extra

# --- CALCOLO QUOTE DETTAGLIATE ---
def calcola_quote(valore):
    return valore * p_p, valore * p_m

q_mutuo_p, q_mutuo_m = calcola_quote(val_mutuo)
q_ele_p, q_ele_m = calcola_quote(val_ele)
q_met_p, q_met_m = calcola_quote(val_metano)
q_acq_p, q_acq_m = calcola_quote(val_acqua)
q_tari_p, q_tari_m = calcola_quote(val_tari)
q_int_p, q_int_m = calcola_quote(val_internet)
q_cibo_p, q_cibo_m = calcola_quote(val_cibo)
q_ext_p, q_ext_m = calcola_quote(val_extra)

tot_quota_p = tot_spese * p_p
tot_quota_m = tot_spese * p_m

with col_graph:
    st.subheader("📈 Proporzione")
    df_pie = pd.DataFrame({"Persona": ["Pierpaolo", "Martina"], "Quota": [tot_quota_p, tot_quota_m]})
    fig = px.pie(df_pie, values='Quota', names='Persona', 
                 color_discrete_sequence=['#1E88E5', '#D81B60'], hole=.4)
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"**Ripartizione:** Pierpaolo {p_p:.1%} | Martina {p_m:.1%}")

# --- RIEPILOGO DETTAGLIATO PERSONE ---
st.divider()
st.subheader("🏁 Riepilogo Versamenti Dettagliato")
c1, c2 = st.columns(2)

with c1:
    st.info("### 👨 Pierpaolo")
    st.write(f"**TOTALE DA VERSARE: {tot_quota_p:.2f} €**")
    with st.expander("Vedi dettaglio quote Pierpaolo"):
        st.write(f"- Mutuo: {q_mutuo_p:.2f} €")
        st.write(f"- Elettricità: {q_ele_p:.2f} €")
        st.write(f"- Metano: {q_met_p:.2f} €")
        st.write(f"- Acqua: {q_acq_p:.2f} €")
        st.write(f"- TARI: {q_tari_p:.2f} €")
        st.write(f"- Internet: {q_int_p:.2f} €")
        st.write(f"- Spesa: {q_cibo_p:.2f} €")
        st.write(f"- Altro: {q_ext_p:.2f} €")

with c2:
    st.error("### 👩 Martina")
    st.write(f"**TOTALE DA VERSARE: {tot_quota_m:.2f} €**")
    with st.expander("Vedi dettaglio quote Martina"):
        st.write(f"- Mutuo: {q_mutuo_m:.2f} €")
        st.write(f"- Elettricità: {q_ele_m:.2f} €")
        st.write(f"- Metano: {q_met_m:.2f} €")
        st.write(f"- Acqua: {q_acq_m:.2f} €")
        st.write(f"- TARI: {q_tari_m:.2f} €")
        st.write(f"- Internet: {q_int_m:.2f} €")
        st.write(f"- Spesa: {q_cibo_m:.2f} €")
        st.write(f"- Altro: {q_ext_m:.2f} €")

# --- BOTTONE SALVATAGGIO ---
st.divider()
if st.button("💾 Salva questo mese su Google Sheets", key="btn_save"):
    nuova_riga = pd.DataFrame([{
        "Data_Salvataggio": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Anno": sel_anno,
        "Mese": sel_mese,
        "Pierpaolo_Tot": tot_p,
        "Martina_Tot": tot_m,
        "Spese_Tot": tot_spese,
        "Quota_P": tot_quota_p,
        "Quota_M": tot_quota_m
    }])
    
    try:
        existing_data = conn.read(spreadsheet=url, worksheet="Dati")
        updated_df = pd.concat([existing_data, nuova_riga], ignore_index=True)
        conn.update(spreadsheet=url, worksheet="Dati", data=updated_df)
        st.success(f"Dati di {sel_mese} {sel_anno} salvati!")
    except Exception as e:
        st.error(f"Errore: {e}")

if st.checkbox("Mostra storico salvato", key="check_history"):
    try:
        st.dataframe(conn.read(spreadsheet=url, worksheet="Dati"))
    except:
        st.warning("Nessun dato nel foglio.")
