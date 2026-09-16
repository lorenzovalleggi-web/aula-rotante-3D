from datetime import date, timedelta
import random
import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="ClassShift • Gestione Banchi",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
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


# --- INIZIALIZZAZIONE SESSION STATE ---
if "elenco_personalizzato" not in st.session_state:
    st.session_state.elenco_personalizzato = ELENCO_BASE.copy()

if "data_selezionata" not in st.session_state:
    oggi = date.today()
    st.session_state.data_selezionata = max(oggi, date(2026, 9, 15))

# STORICO ASSENZE GLOBALI { "YYYY-MM-DD": ["Nome 1", "Nome 2"] }
if "storico_assenze" not in st.session_state:
    st.session_state.storico_assenze = {}

str_data = st.session_state.data_selezionata.strftime("%Y-%m-%d")
if str_data not in st.session_state.storico_assenze:
    st.session_state.storico_assenze[str_data] = []

turno_attuale = ottieni_turno_per_data(st.session_state.data_selezionata)


def ottieni_alunni_ruotati(shift):
    base = st.session_state.elenco_personalizzato.copy()
    shift = shift % len(base)
    return base[-shift:] + base[:-shift]


if "alunni" not in st.session_state:
    st.session_state.alunni = ottieni_alunni_ruotati(turno_attuale["shift"])

# --- FUNZIONI UTILI PER CONTARE LE ASSENZE ---
def calcola_totale_assenze_alunno(nome):
    tot = 0
    for data_str, assenti in st.session_state.storico_assenze.items():
        if nome in assenti:
            tot += 1
    return tot


# --- CSS E STILE ---
st.markdown(
    """
    <style>
    .title-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .title-text { font-size: 22px; font-weight: 800; }
    .badge-container { display: flex; gap: 10px; }
    .badge-presenti { background-color: #059669; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }
    .badge-assenti { background-color: #dc2626; color: white; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: bold; }
    .cattedra-box { background: #0284c7; color: white; text-align: center; padding: 10px; border-radius: 8px; font-weight: 800; font-size: 15px; margin-bottom: 20px; }
    .banco-card { background-color: #ffffff; border: 2px solid #0284c7; border-radius: 8px; padding: 8px 4px; text-align: center; font-weight: bold; color: #0f172a; margin-bottom: 10px; min-height: 65px; display: flex; flex-direction: column; justify-content: center; }
    .banco-triple { border-color: #2563eb; }
    .banco-assente { background-color: #fef2f2 !important; border: 2px solid #dc2626 !important; color: #991b1b !important; }
    .banco-libero { background-color: #f8fafc !important; border: 2px dashed #94a3b8 !important; color: #64748b !important; }
    .posto-label { font-size: 10px; color: #475569; text-transform: uppercase; font-weight: 700; }
    .nome-alunno { font-size: 14px; font-weight: 700; line-height: 1.2; word-break: break-word; }
    .tag-assente { font-size: 10px; color: #dc2626; font-weight: 900; margin-top: 3px; }
    </style>
""",
    unsafe_allow_html=True,
)

# Calcolo assenti del giorno e alunni effettivi
alunni_reali = [
    n for n in st.session_state.elenco_personalizzato if not n.startswith("---")
]
assenti_oggi = st.session_state.storico_assenze[str_data]
tot_assenti = len(assenti_oggi)
tot_presenti = len(alunni_reali) - tot_assenti

st.markdown(
    f"""
    <div class="title-banner">
        <div class="title-text">🚀 ClassShift</div>
        <div class="badge-container">
            <span class="badge-presenti">🟢 Presenti: {tot_presenti}</span>
            <span class="badge-assenti">🔴 Assenti oggi: {tot_assenti}</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- BARRA DEI COMANDI ---
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
        st.rerun()

with c_reset:
    if st.button("🔄 Ripristina", use_container_width=True):
        st.session_state.alunni = ottieni_alunni_ruotati(turno_attuale["shift"])
        st.session_state.storico_assenze[str_data] = []
        st.rerun()

with c_random:
    if st.button("🎲 Casuale", use_container_width=True):
        random.shuffle(st.session_state.alunni)
        st.rerun()

with c_edit:
    with st.popover("✏️ Modifica Nomi"):
        testo_nomi = st.text_area(
            "Nomi Alunni",
            value="\n".join(st.session_state.elenco_personalizzato),
            height=250,
        )
        if st.button("Salva Elenco", type="primary"):
            righe = [
                r.strip() for r in testo_nomi.split("\n") if r.strip()
            ][:19]
            while len(righe) < 19:
                righe.append(f"Posto Libero {len(righe)+1}")
            st.session_state.elenco_personalizzato = righe
            st.session_state.alunni = ottieni_alunni_ruotati(
                turno_attuale["shift"]
            )
            st.rerun()

st.caption(
    f"📌 **Turno {turno_attuale['numero']}** ({turno_attuale['inizio'].strftime('%d/%m/%Y')} - {turno_attuale['fine'].strftime('%d/%m/%Y')})"
)
st.divider()

# SCHEDE
tab_mappa, tab_assenti, tab_report, tab_calendario = st.tabs(
    [
        "🗺️ Mappa Aula",
        "❌ Registro Oggi",
        "📊 Totale Assenze Anno",
        "📅 Turni",
    ]
)

alunni_disposizione = st.session_state.alunni

# --- TAB 1: MAPPA AULA ---
with tab_mappa:
    st.markdown(
        "<div class='cattedra-box'>👨‍🏫 CATTEDRA</div>", unsafe_allow_html=True
    )

    def render_banco(nome, label, is_triple=False):
        e_assente = nome in assenti_oggi
        e_vuoto = "Banco Vuoto" in nome or "Posto Libero" in nome

        css_class = "banco-card"
        if is_triple:
            css_class += " banco-triple"
        if e_assente:
            css_class += " banco-assente"
        elif e_vuoto:
            css_class += " banco-libero"

        return f"""
        <div class='{css_class}'>
            <div class='posto-label'>{label}</div>
            <div class='nome-alunno'>{"<s>" + nome + "</s>" if e_assente else nome}</div>
            {"<div class='tag-assente'>❌ ASSENTE</div>" if e_assente else ""}
        </div>
        """

    st.markdown("##### 📌 Prima Fila - Banco Triplo")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            render_banco(alunni_disposizione[0], "Posto 1", True),
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            render_banco(alunni_disposizione[1], "Posto 2", True),
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            render_banco(alunni_disposizione[2], "Posto 3", True),
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("##### 👥 Banchi Doppi")

    idx = 3
    for f in range(1, 5):
        c_sx1, c_sx2, c_gap, c_dx1, c_dx2 = st.columns([2, 2, 0.4, 2, 2])

        with c_sx1:
            st.markdown(
                render_banco(alunni_disposizione[idx], f"F{f} · SX1"),
                unsafe_allow_html=True,
            )
            idx += 1
        with c_sx2:
            st.markdown(
                render_banco(alunni_disposizione[idx], f"F{f} · SX2"),
                unsafe_allow_html=True,
            )
            idx += 1
        with c_dx1:
            st.markdown(
                render_banco(alunni_disposizione[idx], f"F{f} · DX1"),
                unsafe_allow_html=True,
            )
            idx += 1
        with c_dx2:
            st.markdown(
                render_banco(alunni_disposizione[idx], f"F{f} · DX2"),
                unsafe_allow_html=True,
            )
            idx += 1

# --- TAB 2: REGISTRO OGGI ---
with tab_assenti:
    st.subheader(
        f"📋 Segnala Assenze per il giorno: {st.session_state.data_selezionata.strftime('%d/%m/%Y')}"
    )

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.write("Spunta gli alunni assenti nella data selezionata.")
    with col_btn:
        if st.button("❌ Azzera Oggi", use_container_width=True):
            st.session_state.storico_assenze[str_data] = []
            st.rerun()

    st.divider()

    col_a1, col_a2 = st.columns(2)
    nuovi_assenti_oggi = []

    for i, nome in enumerate(alunni_reali):
        target_col = col_a1 if i % 2 == 0 else col_a2
        tot_anno = calcola_totale_assenze_alunno(nome)
        with target_col:
            is_checked = nome in assenti_oggi
            # Mostra anche il totale anno accanto al nome
            if st.checkbox(
                f"{nome}  *(Totale Anno: {tot_anno})*",
                value=is_checked,
                key=f"chk_{str_data}_{i}_{nome}",
            ):
                nuovi_assenti_oggi.append(nome)

    if nuovi_assenti_oggi != assenti_oggi:
        st.session_state.storico_assenze[str_data] = nuovi_assenti_oggi
        st.rerun()

# --- TAB 3: TOTALE ASSENZE ANNO ---
with tab_report:
    st.subheader("📊 Riepilogo Assenze Anno Scolastico")

    report_data = []
    for nome in alunni_reali:
        tot_giorni = calcola_totale_assenze_alunno(nome)
        report_data.append(
            {
                "Alunno": nome,
                "Totale Giorni Assente": tot_giorni,
            }
        )

    # Ordina per numero di assenze decrescente
    report_data = sorted(
        report_data, key=lambda x: x["Totale Giorni Assente"], reverse=True
    )

    st.dataframe(report_data, use_container_width=True, hide_index=True)

# --- TAB 4: CALENDARIO TURNI ---
with tab_calendario:
    st.subheader("📅 Programmazione Turni A.S. 2026/2027")

    data_turni = []
    for t in TURNI_ANNO:
        e_corrente = (
            "👉 ATTUALE" if t["numero"] == turno_attuale["numero"] else ""
        )
        data_turni.append(
            {
                "Turno": f"Turno {t['numero']}",
                "Inizio": t["inizio"].strftime("%d/%m/%Y"),
                "Fine": t["fine"].strftime("%d/%m/%Y"),
                "Stato": e_corrente,
            }
        )

    st.dataframe(data_turni, use_container_width=True, hide_index=True)
