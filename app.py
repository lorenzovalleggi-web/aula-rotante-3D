

from datetime import date, timedelta
import random
import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="ClassShift • Gestione Banchi", page_icon="🚀", layout="wide"
)

# Elenco iniziale degli alunni
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


def calcola_turno_corrente():
    oggi = date.today()
    inizio_scuola = date(2026, 9, 15)
    fine_scuola = date(2027, 6, 10)

    natale_inizio, natale_fine = date(2026, 12, 24), date(2027, 1, 6)
    pasqua_inizio, pasqua_fine = date(2027, 3, 25), date(2027, 3, 30)

    if oggi < inizio_scuola:
        return 0, inizio_scuola, fine_scuola, True, "Scuola non ancora iniziata"
    if oggi > fine_scuola:
        return 0, inizio_scuola, fine_scuola, True, "Anno scolastico terminato"

    giorni_validi = 0
    curr = inizio_scuola
    while curr <= oggi:
        if not (
            natale_inizio <= curr <= natale_fine
            or pasqua_inizio <= curr <= pasqua_fine
        ):
            giorni_validi += 1
        curr += timedelta(days=1)

    numero_turno = (giorni_validi - 1) // 14
    inizio_t = inizio_scuola + timedelta(days=numero_turno * 14)
    fine_t = inizio_t + timedelta(days=13)
    info_turno = f"Turno N° {numero_turno + 1} ({inizio_t.strftime('%d/%m')} - {fine_t.strftime('%d/%m')})"

    return numero_turno, inizio_scuola, fine_scuola, False, info_turno


num_turno, inizio_scuola, fine_scuola, e_fuori_periodo, info_turno = (
    calcola_turno_corrente()
)


def ottieni_alunni_ruotati(shift):
    base = st.session_state.get("elenco_personalizzato", ELENCO_BASE.copy())
    shift = shift % len(base)
    return base[-shift:] + base[:-shift]


if "elenco_personalizzato" not in st.session_state:
    st.session_state.elenco_personalizzato = ELENCO_BASE.copy()

if "alunni" not in st.session_state:
    st.session_state.alunni = ottieni_alunni_ruotati(num_turno)

st.title("🚀 ClassShift")

# --- BARRA DEI COMANDI ---
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn1:
    if st.button("📅 Ripristina Rotazione 2 Settimane", use_container_width=True):
        st.session_state.alunni = ottieni_alunni_ruotati(num_turno)
        st.success("Disposizione ripristinata!")
with col_btn2:
    if st.button("🎲 Casuale (Estemporaneo)", use_container_width=True):
        random.shuffle(st.session_state.alunni)
        st.success("Disposizione rimescolata!")
with col_btn3:
    with st.popover("✏️ Modifica Elenco Nomi"):
        testo_nomi = st.text_area(
            "Nomi Alunni",
            value="\n".join(st.session_state.elenco_personalizzato),
            height=300,
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

# SCHEDE DI VISUALIZZAZIONE
tab_mappa, tab_elenco = st.tabs(
    ["🗺️ Piantina Mappa Aula", "📋 Vista Elenco Dettagliata"]
)

with tab_mappa:
    # Stile CSS per i banchi grafici
    st.markdown(
        """
        <style>
        .cattedra-box { background-color: #e63946; color: white; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 18px; margin-bottom: 25px; }
        .banco-triple { background-color: #f1faee; border: 2px solid #a8dadc; border-radius: 10px; padding: 10px; text-align: center; font-weight: bold; color: #1d3557; min-height: 70px; }
        .banco-double { background-color: #f8f9fa; border: 2px solid #457b9d; border-radius: 8px; padding: 12px; text-align: center; font-weight: bold; color: #1d3557; margin-bottom: 10px; }
        .posto-label { font-size: 11px; color: #6c757d; text-transform: uppercase; margin-bottom: 4px; }
        .nome-alunno { font-size: 15px; color: #1d3557; }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='cattedra-box'>👨‍🏫 CATTEDRA</div>", unsafe_allow_html=True
    )

    # BANCO TRIPLO
    st.markdown("##### 📌 Prima Fila - Banco Triplo")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"<div class='banco-triple'><div class='posto-label'>Posto 1</div><div class='nome-alunno'>{st.session_state.alunni[0]}</div></div>",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"<div class='banco-triple'><div class='posto-label'>Posto 2</div><div class='nome-alunno'>{st.session_state.alunni[1]}</div></div>",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"<div class='banco-triple'><div class='posto-label'>Posto 3</div><div class='nome-alunno'>{st.session_state.alunni[2]}</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("##### 👥 Banchi Doppi")

    idx = 3
    for f in range(1, 5):
        st.caption(f"Fila {f}")
        c_sx1, c_sx2, c_gap, c_dx1, c_dx2 = st.columns([2, 2, 0.5, 2, 2])

        with c_sx1:
            st.markdown(
                f"<div class='banco-double'><div class='posto-label'>Fila {f} • SX 1</div><div class='nome-alunno'>{st.session_state.alunni[idx]}</div></div>",
                unsafe_allow_html=True,
            )
            idx += 1
        with c_sx2:
            st.markdown(
                f"<div class='banco-double'><div class='posto-label'>Fila {f} • SX 2</div><div class='nome-alunno'>{st.session_state.alunni[idx]}</div></div>",
                unsafe_allow_html=True,
            )
            idx += 1
        with c_dx1:
            st.markdown(
                f"<div class='banco-double'><div class='posto-label'>Fila {f} • DX 1</div><div class='nome-alunno'>{st.session_state.alunni[idx]}</div></div>",
                unsafe_allow_html=True,
            )
            idx += 1
        with c_dx2:
            st.markdown(
                f"<div class='banco-double'><div class='posto-label'>Fila {f} • DX 2</div><div class='nome-alunno'>{st.session_state.alunni[idx]}</div></div>",
                unsafe_allow_html=True,
            )
            idx += 1

with tab_elenco:
    st.subheader("Elenco completo dei posti")
    for i, nome in enumerate(st.session_state.alunni, 1):
        st.write(f"**Posto {i}:** {nome}")
