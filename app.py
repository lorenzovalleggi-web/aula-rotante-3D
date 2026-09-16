from datetime import date, timedelta
import random
import streamlit as st

# Gestore compatibilità versioni Streamlit
def forza_aggiornamento():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# Configurazione della pagina
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

# Palette colori ad alto contrasto per gli avatar dei badge
PALETTE_AVATAR = [
    "#2563eb", "#7c3aed", "#db2777", "#ea580c", 
    "#16a34a", "#0891b2", "#4d7c0f", "#4338ca", 
    "#be185d", "#c2410c", "#15803d", "#0369a1", 
    "#7e22ce", "#b91c1c"
]

def calcola_iniziali(nome_completo):
    """Estrae le iniziali dal nome e cognome (es. 'Calzerano Filippo' -> 'CF')"""
    parti = nome_completo.strip().split()
    if len(parti) >= 2:
        return f"{parti[0][0]}{parti[1][0]}".upper()
    elif len(parti) == 1:
        return parti[0][:2].upper()
    return "??"

def ottieni_colore_avatar(nome_completo):
    """Assegna un colore univoco e fisso ad ogni studente"""
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
                if not (natale_inizio <= curr <= natale_fine or pasqua_inizio <= curr <= pasqua_fine):
                    giorni_lezione += 1
            curr += timedelta(days=1)

        t_fine = curr - timedelta(days=1)
        turni.append({"numero": t_idx, "inizio": t_inizio, "fine": t_fine, "shift": t_idx - 1})
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

def calcola_totale_assenze_alunno(nome):
    tot = 0
    for data_str, assenti in st.session_state.storico_assenze.items():
        if nome in assenti:
            tot += 1
    return tot

# --- CSS BANNER E BADGE ---
st.markdown("""
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

    /* DESIGN BADGE STUDENTE */
    .card-student {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
        transition: all 0.2s;
    }
    .card-absent {
        background: #fef2f2 !important;
        border: 2px solid #ef4444 !important;
    }
    .avatar-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 18px;
        color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        letter-spacing: 1px;
    }
    .student-name {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 10px;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .badge-status-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
    }
    .status-present { background-color: #dcfce7; color: #166534; }
    .status-absent { background-color: #fee2e2; color: #991b1b; }
    .badge-counter { background-color: #f1f5f9; color: #475569; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 12px; border: 1px solid #cbd5e1; }
    </style>
""", unsafe_allow_html=True)

alunni_reali = st.session_state.elenco_personalizzato
assenti_oggi = st.session_state.storico_assenze[str_data]
tot_assenti = len(assenti_oggi)
tot_presenti = len(alunni_reali) - tot_assenti

# BANNER HEADLINE CON ANIMAZIONE
st.markdown(f"""
    <div class="title-banner">
        <div class="banchi-stream">🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑 🪑</div>
        <div class="title-text">🏫 BancoFlow • Classe 3D ({len(alunni_reali)} Alunni)</div>
        <div class="badge-container">
            <span class="badge-presenti">🟢 Presenti: {tot_presenti}</span>
            <span class="badge-assenti">🔴 Assenti oggi: {tot_assenti}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# BARRA COMANDI SUPERIORE
c_data, c_filtro, c_reset, c_edit = st.columns([1.2, 1.2, 1, 1])

with c_data:
    data_scelta = st.date_input(
        "📅 Data:",
        value=st.session_state.data_selezionata,
        min_value=date(2026, 9, 1),
        max_value=date(2027, 6, 10),
        label_visibility="collapsed"
    )
    if data_scelta != st.session_state.data_selezionata:
        st.session_state.data_selezionata = data_scelta
        forza_aggiornamento()

with c_filtro:
    filtro_stato = st.selectbox(
        "Filtra",
        ["Tutti gli Studenti", "Solo Presenti", "Solo Assenti"],
        label_visibility="collapsed"
    )

with c_reset:
    if st.button("🔄 Reset Data", use_container_width=True):
        st.session_state.storico_assenze[str_data] = []
        forza_aggiornamento()

with c_edit:
    with st.popover("✏️ Modifica Nomi"):
        testo_nomi = st.text_area(
            "Nomi Alunni Classe 3D (uno per riga)",
            value="\n".join(st.session_state.elenco_personalizzato),
            height=280
        )
        if st.button("Salva Elenco", type="primary"):
            righe = [r.strip() for r in testo_nomi.split("\n") if r.strip()]
            st.session_state.elenco_personalizzato = righe
            forza_aggiornamento()

st.caption(f"📌 **Anno Scolastico 2026/2027** • Bacheca Badge Studenti e Assenze")
st.divider()

# SEZIONI TAB
tab_badge, tab_report, tab_calendario = st.tabs([
    "📇 Badge Studenti",
    "📊 Report Assenze Anno",
    "📅 Turni Scolastici"
])

# --- TAB 1: BADGE STUDENTI ---
with tab_badge:
    cols = st.columns(4) # Layout a 4 colonne
    
    for idx, nome in enumerate(alunni_reali):
        is_assente = nome in assenti_oggi
        tot_assenze = calcola_totale_assenze_alunno(nome)

        # Gestione filtri visualizzazione
        if filtro_stato == "Solo Presenti" and is_assente:
            continue
        if filtro_stato == "Solo Assenti" and not is_assente:
            continue

        iniziali = calcola_iniziali(nome)
        colore_bg = ottieni_colore_avatar(nome)

        col_target = cols[idx % 4]
        
        with col_target:
            card_class = "card-student card-absent" if is_assente else "card-student"
            badge_status = "<span class='badge-status-tag status-absent'>🔴 Assente</span>" if is_assente else "<span class='badge-status-tag status-present'>🟢 Presente</span>"
            
            st.markdown(f"""
                <div class="{card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="avatar-circle" style="background-color: {colore_bg};">{iniziali}</div>
                        <span class="badge-counter">📊 Assenze: {tot_assenze}</span>
                    </div>
                    <div class="student-name" title="{nome}">{nome}</div>
                    <div style="margin-top: 6px;">{badge_status}</div>
                </div>
            """, unsafe_allow_html=True)
            
            label_btn = "Segna Presente" if is_assente else "Segna Assente"
            type_btn = "secondary" if is_assente else "primary"
            
            if st.button(label_btn, key=f"btn_{idx}_{nome}", use_container_width=True, type=type_btn):
                if is_assente:
                    st.session_state.storico_assenze[str_data].remove(nome)
                else:
                    st.session_state.storico_assenze[str_data].append(nome)
                forza_aggiornamento()

# --- TAB 2: REPORT ANNUALE ---
with tab_report:
    st.subheader("📊 Totale Assenze Accumulate (A.S. 2026/2027)")
    report_data = [
        {"Alunno": nome, "Totale Giorni Assente": calcola_totale_assenze_alunno(nome)}
        for nome in alunni_reali
    ]
    report_data = sorted(report_data, key=lambda x: x["Totale Giorni Assente"], reverse=True)
    st.dataframe(report_data, use_container_width=True, hide_index=True)

# --- TAB 3: CALENDARIO TURNI ---
with tab_calendario:
    st.subheader("📅 Programmazione Turni Rotazione Banchi")
    data_turni = [
        {
            "Turno": f"Turno {t['numero']}",
            "Inizio": t["inizio"].strftime("%d/%m/%Y"),
            "Fine": t["fine"].strftime("%d/%m/%Y"),
            "Stato": "👉 ATTUALE" if t["numero"] == turno_attuale["numero"] else ""
        }
        for t in TURNI_ANNO
    ]
    st.dataframe(data_turni, use_container_width=True, hide_index=True)
