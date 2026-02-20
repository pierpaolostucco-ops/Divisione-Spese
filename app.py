import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Divisione Spese Casa", page_icon="⚖️", layout="wide")

# 2. CONNESSIONE GOOGLE SHEETS
# Utilizziamo un blocco try per assicurarci che i Secrets siano configurati
try:
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ Errore di configurazione: Assicurati di aver inserito l'URL nei Secrets di Streamlit.")
    st.stop()

# 3. SIDEBAR - INPUT STIPENDI
with st.sidebar:
    st.header("📅 Periodo")
    sel_anno = st.selectbox("Anno", [2025, 2026, 2027, 2028], index=1, key="s_anno")
    sel_mese = st.selectbox("Mese", ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                                     "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
                            index=datetime.now().month - 1, key="s_mese")
    
    st.divider()
    st.subheader("👨 Pierpaolo")
    st_p = st.number_input("Stipendio Base (€)", min_value=0.0, value=2000.0, key="val_st_p")
    bo_p = st.number_input("Bonus (€)", min_value=0.0, value=0.0, key="val_bo_p")
    tot_p = st_p + bo_p

    st.subheader("👩 Martina")
    st_m = st.number_input("Stipendio Base (€)", min_value=0.0, value=1500.0, key="val_st_m")
    bo_m = st.number_input("Bonus (€)", min_value=0.0, value=0.0, key="val_bo_m")
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
    st.info(f"**Totale Spese Comuni calcolato: {tot_spese:.2f} €**")

# Calcolo quote finali
q_p = tot_spese * p_p
q_m = tot_spese * p_m

with col_pie:
    st.write("### 📊 Ripartizione Quote")
    df_pie = pd.DataFrame({"Chi": ["Pierpaolo", "Martina"], "Quota": [q_p, q_m]})
    fig_pie = px.pie(df_pie, values='Quota', names='Chi', hole=.4,
                     color_discrete_sequence=['#1f77b4', '#d62728'])
    fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, width="stretch")

# 6. RIEPILOGO VERSAMENTI (Stile pulito con metriche)
st.divider()
st.write("### 🏁 Quote da versare")
r1, r2 = st.columns(2)

with r1:
    st.metric(label="👨 Quota Pierpaolo", value=f"{q_p:.2f} €", delta=f"{p_p:.1%} del peso totale")
    with st.expander("Dettaglio quote Pierpaolo"):
        st.write(f"🏠 Mutuo: {v_mu*p_p:.2f} €")
        st.write(f"🛒 Spesa: {v_cib*p_p:.2f} €")
        st.write(f"🔌 Bollette: {(v_ele+v_met+v_acq+v_int+v_tar)*p_p:.2f} €")

with r2:
    st.metric(label="👩 Quota Martina", value=f"{q_m:.2f} €", delta=f"{p_m:.1%} del peso totale")
    with st.expander("Dettaglio quote Martina"):
        st.write(f"🏠 Mutuo: {v_mu*p_m:.2f} €")
        st.write(f"🛒 Spesa: {v_cib*p_m:.2f} €")
        st.write(f"🔌 Bollette: {(v_ele+v_met+v_acq+v_int+v_tar)*p_m:.2f} €")

# --- 7. SALVATAGGIO ---
st.write("")
col_btn1, col_btn2 = st.columns([2, 1])

with col_btn1:
    if st.button("🚀 SALVA DATI SU GOOGLE SHEETS", use_container_width=True):
        try:
            # Recupero dati attuali
            existing_data = conn.read(spreadsheet=url, worksheet="Dati")
            
            # Prepariamo la nuova riga in modo ultra-pulito
            nuova_riga = pd.DataFrame([{
                "Data": str(datetime.now().strftime("%d/%m/%Y")),
                "Anno": int(sel_anno), 
                "Mese": str(sel_mese),
                "Spese_Tot": round(float(tot_spese), 2), 
                "Quota_P": round(float(q_p), 2), 
                "Quota_M": round(float(q_m), 2)
            }])

            # Forza l'ordine delle colonne
            cols = ["Data", "Anno", "Mese", "Spese_Tot", "Quota_P", "Quota_M"]
            nuova_riga = nuova_riga[cols]

            if existing_data is not None and not existing_data.empty:
                # Se ci sono dati, concatena assicurandosi che le colonne combacino
                updated_df = pd.concat([existing_data[cols], nuova_riga], ignore_index=True)
            else:
                updated_df = nuova_riga

            # Aggiornamento
            conn.update(spreadsheet=url, worksheet="Dati", data=updated_df)
            st.balloons()
            st.success(f"Dati di {sel_mese} salvati correttamente!")
            
        except Exception as e:
            st.error(f"Errore 400 persistente. Prova a premere il tasto 'Reset Intestazioni' a destra.")
            st.info(f"Dettaglio tecnico: {e}")

with col_btn2:
    # TASTO DI EMERGENZA PER RESETTARE IL FOGLIO
    if st.button("⚠️ Reset Intestazioni", help="Usa questo se ricevi Errore 400"):
        try:
            # Crea un foglio vuoto con solo le intestazioni corrette
            df_reset = pd.DataFrame(columns=["Data", "Anno", "Mese", "Spese_Tot", "Quota_P", "Quota_M"])
            conn.update(spreadsheet=url, worksheet="Dati", data=df_reset)
            st.warning("Foglio resettato con le intestazioni corrette! Ora prova a salvare di nuovo.")
        except Exception as e:
            st.error(f"Impossibile resettare: {e}")

# --- 8. ANALISI STORICA ---
st.divider()
if st.checkbox("💾 Visualizza Analisi Storica"):
    try:
        df_history = conn.read(spreadsheet=url, worksheet="Dati")
        if df_history is not None and not df_history.empty:
            # (Mantieni qui il codice del grafico che abbiamo scritto prima...)
            st.write("### 📈 Andamento Mensile")
            fig_history = go.Figure()
            fig_history.add_trace(go.Bar(x=df_history['Mese']+" "+df_history['Anno'].astype(str), y=df_history['Quota_P'], name='Pierpaolo', marker_color='#1f77b4'))
            fig_history.add_trace(go.Bar(x=df_history['Mese']+" "+df_history['Anno'].astype(str), y=df_history['Quota_M'], name='Martina', marker_color='#d62728'))
            fig_history.add_trace(go.Scatter(x=df_history['Mese']+" "+df_history['Anno'].astype(str), y=df_history['Spese_Tot'], name='Totale', line=dict(color='#2ca02c', width=3)))
            fig_history.update_layout(barmode='group')
            st.plotly_chart(fig_history, width="stretch")
            st.dataframe(df_history, width="stretch")
        else:
            st.info("Storico vuoto.")
    except:
        st.warning("Storico non disponibile.")

# 8. ANALISI STORICA E GRAFICO COMBINATO
st.divider()
if st.checkbox("💾 Visualizza Analisi Storica"):
    try:
        df_history = conn.read(spreadsheet=url, worksheet="Dati")
        if not df_history.empty:
            st.write("### 📈 Andamento Mensile")
            
            # Grafico con barre per le quote e linea per il totale
            fig_history = go.Figure()

            # Barre Pierpaolo
            fig_history.add_trace(go.Bar(
                x=df_history['Mese'] + " " + df_history['Anno'].astype(str),
                y=df_history['Quota_P'], name='Quota Pierpaolo', marker_color='#1f77b4'
            ))

            # Barre Martina
            fig_history.add_trace(go.Bar(
                x=df_history['Mese'] + " " + df_history['Anno'].astype(str),
                y=df_history['Quota_M'], name='Quota Martina', marker_color='#d62728'
            ))

            # Linea Totale Spese
            fig_history.add_trace(go.Scatter(
                x=df_history['Mese'] + " " + df_history['Anno'].astype(str),
                y=df_history['Spese_Tot'], name='Totale Spese',
                line=dict(color='#2ca02c', width=3, dash='solid'),
                mode='lines+markers'
            ))

            fig_history.update_layout(
                barmode='group',
                xaxis_title="Mese",
                yaxis_title="Euro (€)",
                legend_title="Legenda",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_history, width="stretch")
            
            st.write("### 📄 Tabella Storica")
            st.dataframe(df_history, width="stretch")
        else:
            st.info("Nessun dato presente nello storico. Effettua il primo salvataggio!")
    except Exception as e:
        st.warning(f"Non è stato possibile caricare lo storico: {e}")



