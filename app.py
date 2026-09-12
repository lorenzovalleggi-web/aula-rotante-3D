import random
import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="Gestione Banchi Classe", page_icon="🏫", layout="wide"
)

# Elenco dei nominativi forniti (18 alunni + 1 posto libero per completare i 19 posti della classe)
ELENCO_INIZIALE = [
    "Calzerano Filippo",
    "Michele Xhaxhi",
    "Luca Ferrari",
    "Massimiliano Vogli",
    "Florent Chickaj",
    "Alice Valleggi",
    "Niccoli Frida",
    "Di Lillo Giulia",
    "Sofia Corradino",
    "Penelope Dell'Isola",
    "Amelia Nuredini",
    "Fornaciai Ginevra",
    "Baldacci Elena",
    "Francesca Basili Pieroni",
    "Carolina Bianchi",
    "Elisa Duli",
    "Luca Tagariello",
    "Derbali Mohamed",
    "--- Posto Libero ---",
]

# Inizializzazione dello stato della sessione
if "alunni" not in st.session_state:
    st.session_state.alunni = ELENCO_INIZIALE.copy()

st.title("🏫 Gestione Rotazione Banchi")
st.caption(
    "Disposizione della classe • 1 banco da 3 posti e 8 banchi da 2 posti"
)

# --- BARRA DEI COMANDI ---
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    if st.button("🔄 Ruota Banchi (Cambio 2 Settimane)", use_container_width=True):
        # Shift circolare: l'ultimo passa in prima posizione
        ultimo = st.session_state.alunni.pop()
        st.session_state.alunni.insert(0, ultimo)
        st.success("Banchi ruotati con successo!")

with col_btn2:
    if st.button("🎲 Casuale", use_container_width=True):
        random.shuffle(st.session_state.alunni)
        st.success("Disposizione rimescolata!")

with col_btn3:
    with st.popover("✏️ Modifica Elenco Nomi"):
        st.write("Inserisci o modifica un nome per riga (massimo 19):")
        testo_nomi = st.text_area(
            "Nomi Alunni",
            value="\n".join(st.session_state.alunni),
            height=300,
            label_visibility="collapsed",
        )
        if st.button("Salva Nomi", type="primary"):
            righe = [
                r.strip() for r in testo_nomi.split("\n") if r.strip()
            ][:19]
            while len(righe) < 19:
                righe.append(f"Posto Libero {len(righe)+1}")
            st.session_state.alunni = righe
            st.rerun()

st.divider()

# --- CATTEDRA ---
st.markdown(
    """
    <div style="background-color: #ff4b4b; color: white; text-align: center; 
                padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 25px;">
        👨‍🏫 CATTEDRA
    </div>
    """,
    unsafe_allow_html=True,
)

# --- BANCO DA TRE ---
st.subheader("📌 Banco Triplo (Prima Fila)")
c1, c2, c3 = st.columns(3)
with c1:
    st.info(f"**Posto 1**\n\n### {st.session_state.alunni[0]}")
with c2:
    st.info(f"**Posto 2**\n\n### {st.session_state.alunni[1]}")
with c3:
    st.info(f"**Posto 3**\n\n### {st.session_state.alunni[2]}")

st.divider()

# --- BANCHI DA DUE (4 FILE) ---
st.subheader("👥 Banchi Doppi")

idx = 3
for fila in range(1, 5):
    st.write(f"**Fila {fila}**")
    col_sx_1, col_sx_2, col_spacer, col_dx_1, col_dx_2 = st.columns(
        [2, 2, 1, 2, 2]
    )

    # Banco SX
    with col_sx_1:
        st.metric(
            label=f"Fila {fila} - Banco SX", value=st.session_state.alunni[idx]
        )
        idx += 1
    with col_sx_2:
        st.metric(
            label=f"Fila {fila} - Banco SX", value=st.session_state.alunni[idx]
        )
        idx += 1

    # Banco DX
    with col_dx_1:
        st.metric(
            label=f"Fila {fila} - Banco DX", value=st.session_state.alunni[idx]
        )
        idx += 1
    with col_dx_2:
        st.metric(
            label=f"Fila {fila} - Banco DX", value=st.session_state.alunni[idx]
        )
        idx += 1

    st.write("")
