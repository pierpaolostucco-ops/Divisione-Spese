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
except Exception as e:
    st.error("⚠️ Errore nei Secrets: Controlla la configurazione del Service Account.")
    st.stop()

# 3. SIDEBAR
with st.sidebar:
    st.header("📅 Periodo")
    sel_anno = st.selectbox("Anno", [2025, 2026, 2027, 2028], index=1, key="sb_anno")
    sel_mese = st.selectbox("Mese", ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                                     "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
                            index=datetime.now().month - 1, key="sb_mese")
    
    st.divider()
    st.subheader("👨 Pierpaolo")
    st_p = st.number_input("Stipendio Base (€)", min_value=0.0, value=2000.0, key="in_st_p")
    bo_p = st.number_input("Bonus (€)", min_value=0.0, value=0.0, key="in_bo_p")
    tot_p = st_p + bo_p

    st.subheader("👩 Martina")
    st_m = st.number_input("Stipendio Base (€)", min_value=0.0, value=1500.0, key="in_st_m")
    bo_m = st.number_input("Bonus (€)", min_value=0.0, value=0.0, key="in_bo_m")
    tot_m = st_m + bo_m

# 4. CALCOLO PERCENTUALI
tot_entrate = tot_p + tot_m
p_p = tot_p / tot_entrate if tot_entrate > 0 else 0.5
p_m = tot_m / tot_entrate if tot_entrate > 0 else 0.5

# 5. LAYOUT PRINCIPALE
st.title("⚖️ Divisione Spese")
st.markdown(f"### Resoconto di **{sel_mese} {sel_anno}**")

col_in, col_pie = st.columns([1.2, 1])

with col_in:
    st.write("### 📝 Inserimento Spese")
    c1, c2 = st.columns(2)
    with c1:
        v_mu = st.number_input("🏠 Mutuo", value=800.0, key="v_mu")
        v_ele = st.number_input("⚡ Elettricità", value=60.0, key="v_ele")
        v_met = st.number_input("🔥 Metano", value=80.0, key="v_met")
        v_acq = st.number_input("💧 Acqua", value=30.0, key="v_acq")
    with c2:
        v_tar = st.number_input("🗑️ TARI", value=0.0, key="v_tar")
        v_int = st.number_input("🌐 Internet", value=30.0, key="v_int")
        v_cib = st.number_input("🛒 Spesa", value=300.0, key="v_cib")
        v_ext = st.number_input("📦 Altro", value=0.0, key="v_ext")
    
    tot_spese = v_mu + v_ele + v_met + v_acq + v_tar + v_int + v_cib + v_ext
    st.info(f"**Totale Spese Comuni: {tot_spese:.2f} €**")

q_p = tot_spese * p_p
q_m = tot_spese * p_m

with col_pie:
    st.write("### 📊 Ripartizione")
    df_pie = pd.DataFrame({"Chi": ["Pierpaolo", "Martina"], "Quota": [q_p, q_m]})
    fig_pie = px.pie(df_pie, values='Quota', names='Chi', hole=.4,
                     color_discrete_sequence=['#1f77b4', '#d62728'])
    st.plotly_chart(fig_pie, width="stretch")

# 6. RIEPILOGO
st.divider()
r1, r2 = st.columns(2)
with r1:
    st.metric(label="👨 Quota Pierpaolo", value=f"{q_p:.2f} €", delta=f"{p_p:.1%}")
with r2:
    st.metric(label="👩 Quota Martina", value=f"{q_m:.2f} €", delta=f"{p_m:.1%}")

# 7. SALVATAGGIO E RESET
st.write("")
col_btn1, col_btn2 = st.columns([2, 1])

with col_btn1:
    if st.button("🚀 SALVA DATI SU GOOGLE SHEETS", use_container_width=True, key="btn_save_main"):
        try:
            existing_data = conn.read(spreadsheet=url, worksheet="Dati")
            nuova_riga = pd.DataFrame([{
                "Data": datetime.now().strftime("%d/%m/%Y"),
                "Anno": int(sel_anno), "Mese": str(sel_mese),
                "Spese_Tot": round(float(tot_spese), 2), 
                "Quota_P": round(float(q_p), 2), "Quota_M": round(float(q_m), 2)
            }])
            cols = ["Data", "Anno", "Mese", "Spese_Tot", "Quota_P", "Quota_M"]
            updated_df = pd.concat([existing_data[cols], nuova_riga[cols]], ignore_index=True) if not existing_data.empty else nuova_riga[cols]
            conn.update(spreadsheet=url, worksheet="Dati", data=updated_df)
            st.balloons()
            st.success("Dati salvati!")
        except Exception as e:
            st.error(f"Errore: {e}")

with col_btn2:
    if st.button("⚠️ Reset Intestazioni", key="btn_reset_emergency"):
        try:
            df_reset = pd.DataFrame(columns=["Data", "Anno", "Mese", "Spese_Tot", "Quota_P", "Quota_M"])
            conn.update(spreadsheet=url, worksheet="Dati", data=df_reset)
            st.warning("Foglio resettato!")
        except Exception as e:
            st.error(f"Errore reset: {e}")

# 8. ANALISI STORICA (Risolto errore duplicato)
st.divider()
# Usiamo una KEY univoca per evitare l'errore DuplicateElementId
if st.checkbox("💾 Visualizza Analisi Storica", key="chk_storico_univoco"):
    try:
        df_history = conn.read(spreadsheet=url, worksheet="Dati")
        if df_history is not None and not df_history.empty:
            st.write("### 📈 Andamento Mensile")
            fig_history = go.Figure()
            # Asse X: combinazione Mese + Anno
            x_axis = df_history['Mese'] + " " + df_history['Anno'].astype(str)
            
            fig_history.add_trace(go.Bar(x=x_axis, y=df_history['Quota_P'], name='Pierpaolo', marker_color='#1f77b4'))
            fig_history.add_trace(go.Bar(x=x_axis, y=df_history['Quota_M'], name='Martina', marker_color='#d62728'))
            fig_history.add_trace(go.Scatter(x=x_axis, y=df_history['Spese_Tot'], name='Totale', line=dict(color='#2ca02c', width=3)))
            
            fig_history.update_layout(barmode='group', hovermode="x unified")
            st.plotly_chart(fig_history, width="stretch")
            st.dataframe(df_history, width="stretch")
        else:
            st.info("Storico vuoto.")
    except Exception as e:
        st.warning(f"Storico non disponibile: {e}")
