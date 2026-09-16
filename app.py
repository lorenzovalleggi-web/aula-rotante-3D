from datetime import date, timedelta
import random
import streamlit as st


# Helper per la compatibilità delle versioni di Streamlit
def forza_aggiornamento():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


# Configurazione pagina
st.set_page_config(
    page_title="BancoFlow • Classe 3D",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Elenco dei 19 alunni della Classe 3D
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
    "Olivieri Ryan",
]

PALETTE_AVATAR = [
    "#2563eb",
    "#7c3aed",
    "#db2777",
    "#ea580c",
    "#16a34a",
    "#0891b2",
    "#4d7c0f",
    "#4338ca",
    "#be185d",
    "#c2410c",
    "#15803d",
    "#0369a1",
    "#7e22ce",
    "#b91c1c",
]


def calcola_iniziali(nome_completo):
    parti = nome_completo.strip().split()
    if len(parti) >= 2:
        return f"{parti[0][0]}{parti[1][0]}".upper()
    elif len(parti) == 1:
        return parti[0][:2].upper()
    return "??"


def ottieni_colore_avatar(nome_completo):
    hash_val = sum(ord(char) for char in nome_completo)
    return PALETTE_AVATAR[hash_val % len(PALETTE_AVATAR)]


# --- LOGICA CALENDARIO E TURNI ---
def calcola_tutti_i_turni():
    inizio_scuola = date(2026, 9, 15)
    fine_scuola = date(2027, 6, 10)
    natale_inizio, natale_fine = date(2026, 12, 24), date(2027, 1, 6)
    pasqua_inizio, pasqua_fine = date(2027, 3, 25), date(2027, 3, 30)

    turni = []
    curr = inizio_scuola
    t_idx = 1

    while curr <= fine_scuola:
        t_inizio = curr
        giorni_lezione = 0

        while giorni_lezione < 10 and curr <= fine_scuola:
            if curr.weekday() < 5:
                if not (
                    natale_inizio <= curr <= natale_fine
                    or pasqua_inizio <= curr <= pasqua_fine
                ):
                    giorni_lezione += 1
            curr += timedelta(days=1)

        t_fine = curr - timedelta(days=1)
        turni.append(
            {"numero": t_idx, "inizio": t_inizio, "fine": t_fine, "shift": t_idx - 1}
        )
        t_idx += 1

    return turni


TURNI_ANNO = calcola_tutti_i_turni()


def ottieni_turno_per_data(data_target):
    if data_target < TURNI_ANNO[0]["inizio"]:
        return TURNI_ANNO[0]
    for t in TURNI_ANNO:
        if t["inizio"] <= data_target <= t["fine"]:
            return t
    return TURNI_ANNO[-1]


# --- SESSION STATE ---
if "elenco_personalizzato" not in st.session_state:
    st.session_state.elenco_personalizzato = ELENCO_BASE.copy()

if "data_selezionata" not in st.session_state:
    oggi = date.today()
    st.session_state.data_selezionata = max(oggi, date(2026, 9, 15))

if "storico_assenze" not in st.session_state:
    st.session_state.storico_assenze = {}

str_data = st.session_state.data_selezionata.strftime("%Y-%m-%d")
if str_data not in st.session_state.storico_assenze:
    st.session_state.storico_assenze[str_data] = []

turno_attuale = ottieni_turno_per_data(st.session_state.data_selezionata)


def ottieni_alunni_ruotati(shift):
    base = st.session_state.elenco_personalizzato.copy()
    if not base:
        return []
    shift = shift % len(base)
    return base[-shift:] + base[:-shift]


if "alunni" not in st.session_state:
    st.session_state.alunni = ottieni_alunni_ruotati(turno_attuale["shift"])


def calcola_totale_assenze_alunno(nome):
    tot = 0
    for data_str, assenti in st.session_state.storico_assenze.items():
        if nome in assenti:
            tot += 1
    return tot


# --- STILI CSS ---
st.markdown(
    """
    <style>
    @keyframes scorriBanchi {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    .title-banner {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        overflow: hidden;
    }
    
    .banchi-stream {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        white-space: nowrap;
        opacity: 0.15;
        pointer-events: none;
        animation: scorriBanchi 12s linear infinite;
        font-size: 24px;
        letter-spacing: 25px;
    }

    .title-text { font-size: 22px; font-weight: 800; z-index: 2; }
    .badge-container { display: flex; gap: 10px; z-index: 2; }
    .badge-presenti { background-color: #059669; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }
    .badge-assenti { background-color: #dc2626; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }

    .cattedra-box {
        background: #0284c7;
        color: white;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 16px;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }

    .card-student {
        background: #ffffff;
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 8px;
        transition: all 0.2s;
    }
    .card-triple-style {
        border-color: #2563eb !important;
        background-color: #f8fafc;
    }
    .card-absent {
        background: #fef2f2 !important;
        border: 2px solid #ef4444 !important;
    }
    .avatar-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 15px;
        color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .posto-label {
        font-size: 10px;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 700;
    }
    .student-name {
        font-size: 14px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 6px;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .badge-counter {
        background-color: #f1f5f9;
        color: #475569;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }
    </style>
""",
    unsafe_allow_html=True,
)

alunni_reali = st.session_state.elenco_personalizzato
assenti_oggi = st.session_state.storico_assenze[str_data]
tot_assenti = len(assenti_oggi)
tot_presenti = len(alunni_reali) - tot_assenti

# BANNER HEADLINE
st.markdown(
    f"""
    <div class="title-banner">
        <div class="banchi-stream">🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑</div>
        <div class="title-text">🏫 BancoFlow • Classe 3D ({len(alunni_reali)} Alunni)</div>
        <div class="badge-container">
            <span class="badge-presenti">🟢 Presenti: {tot_presenti}</span>
            <span class="badge-assenti">🔴 Assenti oggi: {tot_assenti}</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# BARRA COMANDI SUPERIORE
c_data, c_reset, c_random, c_edit = st.columns([1.3, 1, 1, 1])

with c_data:
    data_scelta = st.date_input(
        "📅 Data:",
        value=st.session_state.data_selezionata,
        min_value=date(2026, 9, 1),
        max_value=date(2027, 6, 10),
        label_visibility="collapsed",
    )
    if data_scelta != st.session_state.data_selezionata:
        st.session_state.data_selezionata = data_scelta
        t_nuovo = ottieni_turno_per_data(data_scelta)
        st.session_state.alunni = ottieni_alunni_ruotati(t_nuovo["shift"])
        forza_aggiornamento()

with c_reset:
    if st.button("🔄 Ripristina", use_container_width=True):
        st.session_state.alunni = ottieni_alunni_ruotati(turno_attuale["shift"])
        st.session_state.storico_assenze[str_data] = []
        forza_aggiornamento()

with c_random:
    if st.button("🎲 Casuale", use_container_width=True):
        random.shuffle(st.session_state.alunni)
        forza_aggiornamento()

with c_edit:
    with st.popover("✏️ Modifica Nomi"):
        testo_nomi = st.text_area(
            "Nomi Alunni Classe 3D (uno per riga)",
            value="\n".join(st.session_state.elenco_personalizzato),
            height=280,
        )
        if st.button("Salva Elenco", type="primary"):
            righe = [r.strip() for r in testo_nomi.split("\n") if r.strip()]
            st.session_state.elenco_personalizzato = righe
            st.session_state.alunni = ottieni_alunni_ruotati(
                turno_attuale["shift"]
            )
            forza_aggiornamento()

st.caption(
    f"📌 **Turno {turno_attuale['numero']}** ({turno_attuale['inizio'].strftime('%d/%m/%Y')} - {turno_attuale['fine'].strftime('%d/%m/%Y')})"
)
st.divider()

# SEZIONI TAB
tab_mappa, tab_report, tab_calendario = st.tabs(
    ["🗺️ Disposizione Banchi Aula", "📊 Report Assenze Anno", "📅 Turni Scolastici"]
)

alunni_disposizione = st.session_state.alunni


# Funzione di rendering della Card Banchi
def render_banco_card(nome, label_posto, is_triple=False):
    is_assente = nome in assenti_oggi
    tot_assenze = calcola_totale_assenze_alunno(nome)
    iniziali = calcola_iniziali(nome)
    colore_bg = ottieni_colore_avatar(nome)

    card_class = "card-student"
    if is_triple:
        card_class += " card-triple-style"
    if is_assente:
        card_class += " card-absent"

    nome_visibile = f"<s>{nome}</s>" if is_assente else nome

    st.markdown(
        f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div class="avatar-circle" style="background-color: {colore_bg};">{iniziali}</div>
                <div style="text-align: right;">
                    <div class="posto-label">{label_posto}</div>
                    <span class="badge-counter">📊 {tot_assenze} ass.</span>
                </div>
            </div>
            <div class="student-name" title="{nome}">{nome_visibile}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    label_btn = "Segna Presente" if is_assente else "Segna Assente"
    type_btn = "secondary" if is_assente else "primary"
    key_pulsante = f"btn_map_{str_data}_{nome.replace(' ', '_')}"

    if st.button(
        label_btn, key=key_pulsante, use_container_width=True, type=type_btn
    ):
        if is_assente:
            st.session_state.storico_assenze[str_data].remove(nome)
        else:
            st.session_state.storico_assenze[str_data].append(nome)
        forza_aggiornamento()


# --- TAB 1: MAPPA AULA CON BANCHI ---
with tab_mappa:
    st.markdown(
        "<div class='cattedra-box'>👨‍🏫 CATTEDRA</div>", unsafe_allow_html=True
    )

    # PRIMA FILA: BANCO TRIPLO
    st.markdown("##### 📌 Prima Fila - Banco Triplo")
    m1, m2, m3 = st.columns(3)
    if len(alunni_disposizione) >= 1:
        with m1:
            render_banco_card(alunni_disposizione[0], "Posto 1", True)
    if len(alunni_disposizione) >= 2:
        with m2:
            render_banco_card(alunni_disposizione[1], "Posto 2", True)
    if len(alunni_disposizione) >= 3:
        with m3:
            render_banco_card(alunni_disposizione[2], "Posto 3", True)

    st.write("")
    st.markdown("##### 👥 Banchi Doppi")

    # FILE SUCCESSIVE: BANCHI DOPPI
    idx = 3
    for f in range(1, 5):
        c_sx1, c_sx2, c_gap, c_dx1, c_dx2 = st.columns([2, 2, 0.4, 2, 2])

        if idx < len(alunni_disposizione):
            with c_sx1:
                render_banco_card(alunni_disposizione[idx], f"F{f} · SX1")
                idx += 1
        if idx < len(alunni_disposizione):
            with c_sx2:
                render_banco_card(alunni_disposizione[idx], f"F{f} · SX2")
                idx += 1
        if idx < len(alunni_disposizione):
            with c_dx1:
                render_banco_card(alunni_disposizione[idx], f"F{f} · DX1")
                idx += 1
        if idx < len(alunni_disposizione):
            with c_dx2:
                render_banco_card(alunni_disposizione[idx], f"F{f} · DX2")
                idx += 1

# --- TAB 2: REPORT ANNUALE ---
with tab_report:
    st.subheader("📊 Totale Assenze Accumulate (A.S. 2026/2027)")
    report_data = [
        {"Alunno": nome, "Totale Giorni Assente": calcola_totale_assenze_alunno(nome)}
        for nome in alunni_reali
    ]
    report_data = sorted(
        report_data, key=lambda x: x["Totale Giorni Assente"], reverse=True
    )
    st.dataframe(report_data, use_container_width=True, hide_index=True)

# --- TAB 3: CALENDARIO TURNI ---
with tab_calendario:
    st.subheader("📅 Programmazione Turni Rotazione Banchi")
    data_turni = [
        {
            "Turno": f"Turno {t['numero']}",
            "Inizio": t["inizio"].strftime("%d/%m/%Y"),
            "Fine": t["fine"].strftime("%d/%m/%Y"),
            "Stato": "👉 ATTUALE" if t["numero"] == turno_attuale["numero"] else "",
        }
        for t in TURNI_ANNO
    ]
    st.dataframe(data_turni, use_container_width=True, hide_index=True)
