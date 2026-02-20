import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Divisione Spese", page_icon="⚖️", layout="wide")

# 2. STILE CSS "LIGHT MODERNO"
st.markdown("""
    <style>
    .main { background-color: #F0F2F5; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #007AFF;
        color: white;
        font-weight: bold;
        border: none;
        height: 3em;
    }
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #EAEAEA;
    }
    h1, h2, h3 { color: #1C1C1E; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNESSIONE GOOGLE SHEETS
# Prende l'URL direttamente dai Secrets
try:
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Configura l'URL nei Secrets di Streamlit!")
    st.stop()

# 4. SIDEBAR - INPUT
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

# 5. CALCOLO PERCENTUALI
tot_entrate = tot_p + tot_m
p_p = tot_p / tot_entrate if tot_entrate > 0 else 0.5
p_m = tot_m / tot_entrate if tot_entrate > 0 else 0.5

# 6. LAYOUT CENTRALE
st.title("⚖️ Divisione Spese")
st.markdown(f"### {sel_mese} {sel_anno}")

col_in, col_pie = st.columns([1.2, 1])

with col_in:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.subheader("📝 Inserimento Spese")
    c1, c2 = st.columns(2)
    with c1:
        v_mu = st.number_input("🏠 Mutuo", value=800.0)
        v_el = st.number_input("⚡ Elettricità", value=60.0)
        v_me = st.number_input("🔥 Metano", value=80.0)
        v_ac = st.number_input("💧 Acqua", value=30.0)
    with c2:
        v_ta = st.number_input("🗑️ TARI", value=0.0)
        v_it = st.number_input("🌐 Internet", value=30.0)
        v_ci = st.number_input("🛒 Spesa", value=300.0)
        v_ex = st.number_input("📦 Altro", value=0.0)
    
    tot_spese = v_mu + v_el + v_me + v_ac + v_ta + v_it + v_ci + v_ex
    st.markdown(f"**Totale da dividere: {tot_spese:.2f} €**")
    st.markdown('</div>', unsafe_allow_html=True)

q_p = tot_spese * p_p
q_m = tot_spese * p_m

with col_pie:
    df_pie = pd.DataFrame({"Chi": ["Pierpaolo", "Martina"], "Quota": [q_p, q_m]})
    fig_pie = px.pie(df_pie, values='Quota', names='Chi', hole=.5,
                     color_discrete_sequence=['#007AFF', '#FF2D55'])
    fig_pie.update_layout(margin=dict(t=20, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, width="stretch")

# 7. RIEPILOGO VERSAMENTI
st.divider()
r1, r2 = st.columns(2)

with r1:
    st.markdown(f'<div class="result-card" style="border-left: 5px solid #007AFF;">'
                f'<h3>👨 Pierpaolo</h3>'
                f'<h2>{q_p:.2f} €</h2>'
                f'<p style="color:gray;">Sulla base di {p_p:.1%} delle entrate</p>'
                f'</div>', unsafe_allow_html=True)

with r2:
    st.markdown(f'<div class="result-card" style="border-left: 5px solid #FF2D55;">'
                f'<h3>👩 Martina</h3>'
                f'<h2>{q_m:.2f} €</h2>'
                f'<p style="color:gray;">Sulla base di {p_m:.1%} delle entrate</p>'
                f'</div>', unsafe_allow_html=True)

# 8. TASTO SALVATAGGIO
if st.button("🚀 Salva Dati su Google Sheets"):
    nuova_riga = pd.DataFrame([{
        "Data": datetime.now().strftime("%d/%m/%Y"),
        "Anno": sel_anno, "Mese": sel_mese,
        "P_Tot": tot_p, "M_Tot": tot_m,
        "Spese_Tot": tot_spese, "Quota_P": q_p, "Quota_M": q_m
    }])
    try:
        existing = conn.read(spreadsheet=url, worksheet="Dati")
        updated = pd.concat([existing, nuova_riga], ignore_index=True)
        conn.update(spreadsheet=url, worksheet="Dati", data=updated)
        st.balloons()
        st.success("Dati archiviati con successo!")
    except Exception as e:
        st.error(f"Errore: {e}")

# 9. STORICO E GRAFICO A BARRE
st.divider()
if st.checkbox("💾 Visualizza Storico e Analisi"):
    try:
        data_storico = conn.read(spreadsheet=url, worksheet="Dati")
        
        if not data_storico.empty:
            st.subheader("📊 Confronto Mesi (Quota Pierpaolo vs Martina)")
            
            # Prepariamo i dati per il grafico a barre
            # Trasformiamo il dataframe da "largo" a "lungo" per Plotly
            df_melt = data_storico.melt(id_vars=['Mese', 'Anno'], 
                                        value_vars=['Quota_P', 'Quota_M'],
                                        var_name='Partner', value_name='Euro')
            df_melt['Partner'] = df_melt['Partner'].replace({'Quota_P': 'Pierpaolo', 'Quota_M': 'Martina'})
            df_melt['Periodo'] = df_melt['Mese'] + " " + df_melt['Anno'].astype(str)

            fig_bar = px.bar(df_melt, x='Periodo', y='Euro', color='Partner',
                             barmode='group', 
                             color_discrete_map={'Pierpaolo': '#007AFF', 'Martina': '#FF2D55'},
                             text_auto='.2s')
            
            st.plotly_chart(fig_bar, width="stretch")
            
            st.subheader("📄 Dettaglio Tabella")
            st.dataframe(data_storico, width="stretch")
        else:
            st.info("Lo storico è ancora vuoto.")
    except:
        st.warning("Impossibile caricare lo storico.")
