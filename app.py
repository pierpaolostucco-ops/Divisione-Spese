import streamlit as st

st.set_page_config(page_title="Finance di Coppia", page_icon="💰")

st.title("💰 Gestione Spese Equa")
st.write("Calcola la divisione delle spese basata sulla proporzionalità degli stipendi.")

# --- SEZIONE INPUT STIPENDI ---
st.subheader("1. Inserite i vostri stipendi netti")
col1, col2 = st.columns(2)
with col1:
    stip_a = st.number_input("Stipendio Partner A (€)", min_value=0.0, value=1800.0, step=50.0)
with col2:
    stip_b = st.number_input("Stipendio Partner B (€)", min_value=0.0, value=1200.0, step=50.0)

tot_entrate = stip_a + stip_b

if tot_entrate > 0:
    perc_a = stip_a / tot_entrate
    perc_b = stip_b / tot_entrate
else:
    perc_a = perc_b = 0.5

# Mostra le percentuali calcolate
st.info(f"**Ripartizione:** Partner A: {perc_a:.1%} | Partner B: {perc_b:.1%}")

st.divider()

# --- SEZIONE SPESE ---
st.subheader("2. Inserite le spese comuni")
mutuo = st.number_input("Mutuo / Affitto (€)", min_value=0.0, value=700.0)
bollette = st.number_input("Totale Bollette (Luce, Gas, Acqua) (€)", min_value=0.0, value=150.0)
altre_spese = st.number_input("Altre spese (Spesa, Internet, ecc.) (€)", min_value=0.0, value=200.0)

tot_spese = mutuo + bollette + altre_spese

# --- RISULTATI FINALI ---
st.divider()
st.subheader("3. Quote da versare")

quota_a = tot_spese * perc_a
quota_b = tot_spese * perc_b

c1, c2 = st.columns(2)
c1.metric("Partner A paga:", f"{quota_a:.2f} €")
c2.metric("Partner B paga:", f"{quota_b:.2f} €")

st.warning(f"**Totale da versare sul conto comune:** {tot_spese:.2f} €")