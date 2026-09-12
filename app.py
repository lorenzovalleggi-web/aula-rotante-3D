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


# --- LOGICA DEL CALENDARIO E DEI TURNI ---
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
        dias_contati = 0

        while dias_contati < 14 and curr <= fine_scuola:
            if not (
                natale_inizio <= curr <= natale_fine
                or pasqua_inizio <= curr <= pasqua_fine
            ):
                dias_contati += 1
            curr += timedelta(days=1)

        t_fine = curr - timedelta(days=1)
        turni.append(
            {"numero": t_idx, "inizio": t_inizio, "fine": t_fine, "shift": t_idx - 1}
        )
        t_idx += 1

    return turni


TURNI_ANNO = calcola_tutti_i_turni()


def ottieni_turno_per_data(data_target):
    for t in TURNI_ANNO:
        if t["inizio"] <= data_target <= t["fine"]:
            return t
    if data_target < TURNI_ANNO[0]["inizio"]:
        return TURNI_ANNO[0]
    return TURNI_ANNO[-1]


# Inizializzazione Session State
if "elenco_personalizzato" not in st.session_state:
    st.session_state.elenco_personalizzato = ELENCO_BASE.copy()

if "assenti" not in st.session_state:
    st.session_state.assenti = []

if "data_selezionata" not in st.session_state:
    st.session_state.data_selezionata = date.today()

turno_attuale = ottieni_turno_per_data(st.session_state.data_selezionata)


def ottieni_alunni_ruotati(shift):
    base = st.session_state.elenco_personalizzato.copy()
    shift = shift % len(base)
    return base[-shift:] + base[:-shift]


if "alunni" not in st.session_state:
    st.session_state.alunni = ottieni_alunni_ruotati(turno_attuale["shift"])

# --- HEADER APP ---
st.title("🚀 ClassShift")

# --- BARRA SUPERIORE DEI COMANDI ---
col_c1, col_c2, col_c3, col_c4 = st.columns([1.2, 1, 1, 1])

with col_c1:
    data_scelta = st.date_input(
        "📅 Data di riferimento:",
        value=st.session_state.data_selezionata,
        min_value=date(2026, 9, 15),
        max_value=date(2027, 6, 10),
    )
    if data_scelta != st.session_state.data_selezionata:
        st.session_state.data_selezionata = data_scelta
        t_nuovo = ottieni_turno_per_data(data_scelta)
        st.session_state.alunni = ottieni_alunni_ruotati(t_nuovo["shift"])
        st.rerun()

with col_c2:
    if st.button("🔄 Ripristina Calendario", use_container_width=True):
        st.session_state.alunni = ottieni_alunni_ruotati(turno_attuale["shift"])
        st.success("Mappa ripristinata!")

with col_c3:
    if st.button("🎲 Casuale (Estemporaneo)", use_container_width=True):
        random.shuffle(st.session_state.alunni)
        st.success("Disposizione rimescolata!")

with col_c4:
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
            st.session_state.alunni = ottieni_alunni_ruotati(
                turno_attuale["shift"]
            )
            st.rerun()

st.caption(
    f"📌 **Turno N° {turno_attuale['numero']}** (Valido dal {turno_attuale['inizio'].strftime('%d/%m/%Y')} al {turno_attuale['fine'].strftime('%d/%m/%Y')})"
)
st.divider()

# SCHEDE DI NAVIGAZIONE
tab_mappa, tab_assenti, tab_calendario = st.tabs(
    [
        "🗺️ Piantina Mappa Aula",
        "❌ Segnala Assenze",
        "📅 Calendario Turni Anno",
    ]
)

# --- TAB 1: MAPPA AULA ADATTATA MOBILE ---
with tab_mappa:
    # CSS per forzare il layout a griglia/banchi affiancati anche su smartphone
    st.markdown(
        """
        <style>
        /* Forzo le colonne ad affiancarsi anche su mobile */
        [data-testid="column"] {
            min-width: 0 !important;
            flex: 1 1 0px !important;
        }
        
        .cattedra-box { 
            background-color: #e63946; 
            color: white; 
            text-align: center; 
            padding: 8px; 
            border-radius: 6px; 
            font-weight: bold; 
            font-size: 16px; 
            margin-bottom: 15px; 
        }
        
        .banco-triple, .banco-double { 
            background-color: #ffffff; 
            border: 2px solid #457b9d; 
            border-radius: 6px; 
            padding: 6px 2px; 
            text-align: center; 
            font-weight: bold; 
            color: #1d3557; 
            margin-bottom: 8px; 
            min-height: 60px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .banco-triple {
            border-color: #a8dadc;
        }
        
        .banco-assente { 
            background-color: #ffe6e6 !important; 
            border-color: #ff4d4d !important; 
            color: #cc0000 !important; 
        }
        
        .posto-label { 
            font-size: 9px; 
            color: #6c757d; 
            text-transform: uppercase; 
            margin-bottom: 2px; 
            line-height: 1.1;
        }
        
        .nome-alunno { 
            font-size: 12px; 
            line-height: 1.2;
            word-break: break-word;
        }
        
        .tag-assente { 
            font-size: 9px; 
            color: #d90429; 
            font-weight: bold; 
            margin-top: 2px; 
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='cattedra-box'>👨‍🏫 CATTEDRA</div>", unsafe_allow_html=True
    )

    def render_banco(nome, label, is_triple=False):
        e_assente = nome in st.session_state.assenti
        css_class = "banco-triple" if is_triple else "banco-double"
        if e_assente:
            css_class += " banco-assente"

        html_content = f"""
        <div class='{css_class}'>
            <div class='posto-label'>{label}</div>
            <div class='nome-alunno'>{"<s>" + nome + "</s>" if e_assente else nome}</div>
            {"<div class='tag-assente'>❌ ASSENTE</div>" if e_assente else ""}
        </div>
        """
        return html_content

    # BANCO TRIPLO
    st.markdown("##### 📌 Prima Fila - Banco Triplo")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            render_banco(st.session_state.alunni[0], "Posto 1", True),
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            render_banco(st.session_state.alunni[1], "Posto 2", True),
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            render_banco(st.session_state.alunni[2], "Posto 3", True),
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("##### 👥 Banchi Doppi")

    idx = 3
    for f in range(1, 5):
        st.caption(f"Fila {f}")
        c_sx1, c_sx2, c_gap, c_dx1, c_dx2 = st.columns([2, 2, 0.4, 2, 2])

        with c_sx1:
            st.markdown(
                render_banco(st.session_state.alunni[idx], f"F{f} · SX1"),
                unsafe_allow_html=True,
            )
            idx += 1
        with c_sx2:
            st.markdown(
                render_banco(st.session_state.alunni[idx], f"F{f} · SX2"),
                unsafe_allow_html=True,
            )
            idx += 1
        with c_dx1:
            st.markdown(
                render_banco(st.session_state.alunni[idx], f"F{f} · DX1"),
                unsafe_allow_html=True,
            )
            idx += 1
        with c_dx2:
            st.markdown(
                render_banco(st.session_state.alunni[idx], f"F{f} · DX2"),
                unsafe_allow_html=True,
            )
            idx += 1

# --- TAB 2: SEGNALA ASSENZE ---
with tab_assenti:
    st.subheader("📋 Registro Assenze")
    st.write("Spunta gli alunni assenti:")

    alunni_effettivi = [
        n
        for n in st.session_state.elenco_personalizzato
        if not n.startswith("---")
    ]
    col_a1, col_a2 = st.columns(2)

    nuovi_assenti = []
    for i, nome in enumerate(alunni_effettivi):
        target_col = col_a1 if i % 2 == 0 else col_a2
        with target_col:
            is_checked = nome in st.session_state.assenti
            if st.checkbox(
                nome, value=is_checked, key=f"chk_{i}_{nome}"
            ):
                nuovi_assenti.append(nome)

    st.session_state.assenti = nuovi_assenti

    if st.button("Reset Tutte le Assenze"):
        st.session_state.assenti = []
        st.rerun()

# --- TAB 3: CALENDARIO ANNUALE TURNI ---
with tab_calendario:
    st.subheader("📅 Programmazione Turni A.S. 2026/2027")

    data_turni = []
    for t in TURNI_ANNO:
        e_corrente = "👉 ATTUALE" if t["numero"] == turno_attuale["numero"] else ""
        data_turni.append(
            {
                "Turno": f"Turno {t['numero']}",
                "Inizio": t["inizio"].strftime("%d/%m/%Y"),
                "Fine": t["fine"].strftime("%d/%m/%Y"),
                "Stato": e_corrente,
            }
        )

    st.dataframe(data_turni, use_container_width=True, hide_index=True)


    
