import streamlit as st
import random
import time
from datetime import datetime, timedelta

# --- KONFIGURACIJA ---
UKUPNO_SLICICA = 385
SLICICA_U_PAKETU = 4
CEKANJE_MINUTA = 30

st.set_page_config(page_title="Zagor Digitalni Album", layout="wide")

# CSS za malo bolji izgled
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #f63366; color: white; }
    .stImage { border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

# --- STANJE APLIKACIJE ---
if 'album' not in st.session_state:
    st.session_state.album = {}  # {broj_slicice: kolicina}
    st.session_state.paketi = 5
    st.session_state.zadnji_refill = datetime.now()

# Logika za nove paketiće svako pola sata
prolo_vremena = datetime.now() - st.session_state.zadnji_refill
if prolo_vremena > timedelta(minutes=CEKANJE_MINUTA):
    dodatni = int(prolo_vremena.total_seconds() // (CEKANJE_MINUTA * 60)) * 2
    st.session_state.paketi += dodatni
    st.session_state.zadnji_refill = datetime.now()

# --- HEADER ---
st.title("🪓 Zagor Te-Nay: Digitalni Kolekcionar")
col1, col2, col3 = st.columns(3)
col1.metric("Sakupljeno", f"{len(st.session_state.album)} / {UKUPNO_SLICICA}")
col2.metric("Dostupni Paketići", st.session_state.paketi)
col3.write(f"Sljedeći paketi stižu u: **{(st.session_state.zadnji_refill + timedelta(minutes=CEKANJE_MINUTA)).strftime('%H:%M')}**")

# --- OTVARANJE PAKETIĆA ---
if st.button("📦 OTVORI PAKETIĆ (4 SLIČICE)"):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)]
        
        # Mala animacija
        placeholder = st.empty()
        placeholder.video("https://www.w3schools.com/html/mov_bbb.mp4") # Ovdje može ići bilo koji kratki efekt
        time.sleep(1)
        placeholder.empty()

        st.subheader("Dobio si:")
        prikaz_cols = st.columns(4)
        for i, br in enumerate(nove):
            st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
            with prikaz_cols[i]:
                # Linkovi na slike (koristimo placeholder dok ne mapiramo stripovi.com ID-ove)
                st.image(f"https://placehold.co/200x300/orange/white?text=Zagor+{br}", caption=f"Naslovnica #{br}")
        st.balloons()
    else:
        st.warning("Nemaš više paketića! Strpi se malo, Duh sa sjekirom ih upravo sprema.")

# --- PRIKAZ ALBUMA ---
st.divider()
stranica = st.select_slider("Prelistaj album (stranice po 20)", 
                           options=[f"{i}-{i+19}" for i in range(1, UKUPNO_SLICICA, 20)])
start_idx = int(stranica.split("-")[0])

st.subheader(f"Stranica {stranica}")
album_cols = st.columns(5)
for i in range(start_idx, start_idx + 20):
    if i > UKUPNO_SLICICA: break
    kol = (i - start_idx) % 5
    with album_cols[kol]:
        if i in st.session_state.album:
            # Prikaz prave sličice ako je imaš
            st.image(f"https://placehold.co/200x300/black/white?text={i}", caption=f"Imam (x{st.session_state.album[i]})")
        else:
            # Siva slika ako je nemaš
            st.image(f"https://placehold.co/200x300/gray/white?text={i}", caption=f"Fali #{i}")
