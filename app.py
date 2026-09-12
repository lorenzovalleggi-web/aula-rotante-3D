from datetime import date, timedelta
import random
import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="ClassShift • Gestione Banchi", page_icon="🚀", layout="wide"
)

# Elenco iniziale degli alunni (18 alunni + 1 posto libero)
ELENCO_BASE = [
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


# --- CALCOLO GIORNI EFFETTIVI DI LEZIONE E TURNO ---
def calcola_turno_corrente():
    oggi = date.today()
    inizio_scuola = date(2026, 9, 15)
    fine_scuola = date(2027, 6, 10)

    # Date escluse (Vacanze + Festivi rossi)
    festivi_singoli = {
        date(2026, 11, 1),  # Tutti i Santi
        date(2026, 12, 8),  # Immacolata
        date(2027, 4, 25),  # Liberazione
        date(2027, 5, 1),  # Festa del Lavoro
        date(2027, 6, 2),  # Festa della Repubblica
    }

    # Vacanze di Natale 2026 (24 dic 2026 - 6 gen 2027)
    natale_inizio = date(2026, 12, 24)
    natale_fine = date(2027, 1, 6)

    # Vacanze di Pasqua 2027 (25 mar 2027 - 30 mar 2027)
    pasqua_inizio = date(2027, 3, 25)
    pasqua_fine = date(2027, 3, 30)

    # Controllo stato fuori dal periodo scolastico
    if oggi < inizio_scuola:
        return 0, inizio_scuola, fine_scuola, True, "Scuola non ancora iniziata"
    if oggi > fine_scuola:
        return 0, inizio_scuola, fine_scuola, True, "Anno scolastico terminato"

    # Conteggio dei giorni di lezione effettivi dal 15 settembre ad oggi
    giorni_lezione = 0
    curr = inizio_scuola

    while curr <= oggi:
        # Se è sabato (5) o domenica (6), oppure un festivo o vacanza -> non si conta
        if curr.weekday() < 5:  # Lunedì-Venerdì
            is_natale = natale_inizio <= curr <= natale_fine
            is_pasqua = pasqua_inizio <= curr <= pasqua_fine
            is_festivo = curr in festivi_singoli

            if not (is_natale or is_pasqua or is_festivo):
                giorni_lezione += 1
        curr += timedelta(days=1)

    # Ogni turno corrisponde a 10 giorni effettivi di lezione (2 settimane di scuola)
    numero_turno = (giorni_lezione - 1) // 10 if giorni_lezione > 0 else 0

    return numero_turno, inizio_scuola, fine_scuola, False, ""


num_turno, inizio_scuola, fine_scuola, e_fuori_periodo, nota = (
    calcola_turno_corrente()
)


def ottieni_alunni_ruotati(shift):
    if not st.session_state.get("elenco_personalizzato"):
        base = ELENCO_BASE.copy()
    else:
        base = st.session_state.elenco_personalizzato.copy()

    shift = shift % len(base)
    return base[-shift:] + base[:-shift]


# Inizializzazione della sessione
if "elenco_personalizzato" not in st.session_state:
    st.session_state.elenco_personalizzato = ELENCO_BASE.copy()

if "alunni" not in st.session_state:
    st.session_state.alunni = ottieni_alunni_ruotati(num_turno)

# Header App
st.title("🚀 ClassShift")

if e_fuori_periodo:
    st.info(f"ℹ️ {nota} (Periodo di riferimento: 15/09/2026 – 10/06/2027).")
else:
    st.caption(
        f"Anno Scolastico 2026/2027 | **Turno Attuale: N° {num_turno + 1}** (Cambio ogni 10 giorni effettivi di lezione)"
    )

# --- BARRA DEI COMANDI ---
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    if st.button("📅 Ripristina Rotazione Calendario", use_container_width=True):
        st.session_state.alunni = ottieni_alunni_ruotati(num_turno)
        st.success(f"Posizioni aggiornate al Turno {num_turno + 1}!")

with col_btn2:
    if st.button("🎲 Casuale (Estemporaneo)", use_container_width=True):
        random.shuffle(st.session_state.alunni)
        st.success("Disposizione rimescolata per questa sessione!")

with col_btn3:
    with st.popover("✏️ Modifica Elenco Nomi"):
        st.write("Inserisci o modifica un nome per riga (massimo 19):")
        testo_nomi = st.text_area(
            "Nomi Alunni",
            value="\n".join(st.session_state.elenco_personalizzato),
            height=300,
            label_visibility="collapsed",
        )
        if st.button("Salva Nomi", type="primary"):
            righe = [
                r.strip() for r in testo_nomi.split("\n") if r.strip()
            ][:19]
            while len(righe) < 19:
                righe.append(f"Posto Libero {len(righe)+1}")
            st.session_state.elenco_personalizzato = righe
            st.session_state.alunni = ottieni_alunni_ruotati(num_turno)
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
