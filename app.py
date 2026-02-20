import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Divisione Spese PRO", page_icon="⚖️", layout="wide")

# 2. STILE CSS "DARK PRO"
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    .dark-card { background-color: #1C2128; padding: 20px; border-radius: 12px; border: 1px solid #30363D; margin-bottom: 20px; }
    .stNumberInput div div input { background-color: #0D1117 !important; color: white !important; border: 1px solid #30363D !important; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%);
        color: white; font-weight: bold; border: none; padding: 10px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 15px rgba(0, 198, 255, 0.5); color: white; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONNESSIONE GOOGLE SHEETS
# L'URL viene preso dai Secrets se non specificato qui
url = st.secrets["connections"]["gsheets"]["spreadsheet"]
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. SIDEBAR - INPUT STIPENDI
with st.sidebar:
    st.title("⚙️ Setup")
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

# 5. CALCOLO PERCENTUALI
tot_entrate = tot_p + tot_m
p_p = tot_p / tot_entrate if tot_entrate > 0 else 0.5
p_m = tot_m / tot_entrate if tot_entrate > 0 else 0.5

# 6. HEADER DASHBOARD
st.title("⚖️ Divisione Spese (Pierpaolo & Martina)")
st.markdown(f"#### 📊 Dashboard di {sel_mese} {sel_anno}")

# 7. SEZIONE SPESE
col_input, col_graph = st.columns([1.2, 1])

with col_input:
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    st.subheader("📝 Inserimento Costi")
    c1, c2 = st.columns(2)
    with c1:
        val_mutuo = st.number_input("🏠 Mutuo / Affitto", value=800.0, key="in_mutuo")
        val_ele = st.number_input("⚡ Elettricità", value=60.0, key="in_ele")
        val_metano = st.number_input("🔥 Metano", value=80.0, key="in_met")
        val_acqua = st.number_input("💧 Acqua", value=30.0, key="in_acq")
    with c2:
        val_tari = st.number_input("🗑️ TARI", value=0.0, key="in_tari")
        val_internet = st.number_input("🌐 Internet", value=30.0, key="in_int")
        val_cibo = st.number_input("🛒 Spesa Alimentare", value=300.0, key="in_cibo")
        val_extra = st.number_input("📦 Altre Spese", value=0.0, key="in_extra")
    
    tot_spese = val_mutuo + val_ele + val_metano + val_acqua + val_tari + val_internet + val_cibo + val_extra
    st.markdown(f"**TOTALE SPESE COMUNI: {tot_spese:.2f} €**")
    st.markdown('</div>', unsafe_allow_html=True)

# 8. CALCOLO QUOTE DETTAGLIATE
tot_quota_p = tot_spese * p_p
tot_quota_m = tot_spese * p_m

with col_graph:
    st.subheader("📈 Proporzione")
    df_pie = pd.DataFrame({"Persona": ["Pierpaolo", "Martina"], "Quota": [tot_quota_p, tot_quota_m]})
    fig = px.pie(df_pie, values='Quota', names='Persona', color_discrete_sequence=['#58A6FF', '#FF7B72'], hole=.6)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True, margin=dict(t=0,b=0,l=0,r=0))
    # AGGIORNATO: Usiamo width="stretch" come richiesto dalle nuove versioni
    st.plotly_chart(fig, width="stretch")

# 9. RIEPILOGO VERSAMENTI
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.markdown(f'<div class="dark-card" style="border-top: 4px solid #58A6FF;"><h3>👨 Pierpaolo</h3><h2>{tot_quota_p:.2f} €</h2></div>', unsafe_allow_html=True)
    with st.expander("🔍 Dettaglio"):
        st.write(f"🏠 Mutuo: {val_mutuo*p_p:.2f} €")
        st.write(f"🛒 Spesa: {val_cibo*p_p:.2f} €")
        # ... qui puoi aggiungere le altre voci se vuoi vederle tutte espanse

with c2:
    st.markdown(f'<div class="dark-card" style="border-top: 4px solid #FF7B72;"><h3>👩 Martina</h3><h2>{tot_quota_m:.2f} €</h2></div>', unsafe_allow_html=True)
    with st.expander("🔍 Dettaglio"):
        st.write(f"🏠 Mutuo: {val_mutuo*p_m:.2f} €")
        st.write(f"🛒 Spesa: {val_cibo*p_m:.2f} €")

# 10. BOTTONE SALVATAGGIO
st.divider()
if st.button("🚀 Salva su Google Sheets", key="btn_save"):
    nuova_riga = pd.DataFrame([{
        "Data": datetime.now().strftime("%d/%m/%Y"), "Anno": sel_anno, "Mese": sel_mese,
        "P_Tot": tot_p, "M_Tot": tot_m, "Spese": tot_spese, "Q_P": tot_quota_p, "Q_M": tot_quota_m
    }])
    try:
        existing = conn.read(spreadsheet=url, worksheet="Dati")
        updated = pd.concat([existing, nuova_riga], ignore_index=True)
        conn.update(spreadsheet=url, worksheet="Dati", data=updated)
        st.balloons()
        st.success("Dati salvati!")
    except Exception as e:
        st.error(f"Errore: {e}")

if st.checkbox("💾 Mostra storico"):
    # AGGIORNATO: width="stretch" per la tabella
    st.dataframe(conn.read(spreadsheet=url, worksheet="Dati"), width="stretch")
