import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione pagina
st.set_page_config(page_title="Finance di Coppia Pro", page_icon="⚖️", layout="wide")

st.title("⚖️ Calcolatore Spese Equo")
st.markdown("---")

# --- SIDEBAR: INPUT STIPENDI ---
with st.sidebar:
    st.header("💰 Entrate Mensili")
    stip_a = st.number_input("Stipendio Partner A (€)", min_value=0.0, value=2000.0, step=50.0)
    stip_b = st.number_input("Stipendio Partner B (€)", min_value=0.0, value=1500.0, step=50.0)
    
    tot_entrate = stip_a + stip_b
    
    if tot_entrate > 0:
        p_a = stip_a / tot_entrate
        p_b = stip_b / tot_entrate
    else:
        p_a = p_b = 0.5

    st.info(f"**Ripartizione Equa:**\n\nPartner A: {p_a:.1%}\n\nPartner B: {p_b:.1%}")

# --- CORPO CENTRALE: SPESE ---
col_spese, col_grafico = st.columns([1, 1])

with col_spese:
    st.subheader("📝 Elenco Spese Comuni")
    mutuo = st.number_input("Mutuo / Affitto (€)", min_value=0.0, value=800.0)
    bollette = st.number_input("Bollette (Luce, Gas, Acqua) (€)", min_value=0.0, value=150.0)
    spesa_cibo = st.number_input("Spesa Alimentare (€)", min_value=0.0, value=300.0)
    extra = st.number_input("Altre Spese (Internet, Netflix, ecc.) (€)", min_value=0.0, value=50.0)
    
    tot_spese = mutuo + bollette + spesa_cibo + extra

# --- CALCOLI FINALI ---
quota_a = tot_spese * p_a
quota_b = tot_spese * p_b

rimanente_a = stip_a - quota_a
rimanente_b = stip_b - quota_b

with col_grafico:
    st.subheader("📊 Analisi Visiva")
    # Grafico a torta delle quote
    df_grafico = pd.DataFrame({
        "Partner": ["Partner A", "Partner B"],
        "Quota da Pagare (€)": [quota_a, quota_b]
    })
    fig = px.pie(df_grafico, values='Quota da Pagare (€)', names='Partner', 
                 color_discrete_sequence=['#00CC96', '#636EFA'], hole=.3)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- RIASSUNTO METRICHE ---
st.subheader("🏁 Risultato Finale")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Partner A paga", f"{quota_a:.2f} €")
    st.caption(f"Ti restano: **{rimanente_a:.2f} €**")

with c2:
    st.metric("Partner B paga", f"{quota_b:.2f} €")
    st.caption(f"Ti restano: **{rimanente_b:.2f} €**")

with c3:
    st.metric("Totale Spese Comuni", f"{tot_spese:.2f} €", delta_color="inverse")
    st.caption("Fondo comune da versare")

st.success(f"L'equità è garantita: chi guadagna di più ({'Partner A' if stip_a > stip_b else 'Partner B'}) contribuisce proporzionalmente di più.")
