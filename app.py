import streamlit as st
import random
import time
from datetime import datetime, timedelta
import os

# --- 1. KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="Zagor & Cico Digitalni Album",
    page_icon="🪓",
    layout="wide"
)

# --- 2. POSTAVKE ALBUMA ---
# Tutto (239) + Speciale Zagor (38) + Speciale Cico (27) = 304
UKUPNO_SLICICA = 304 
SLICICA_U_PAKETU = 4
POCETNI_PAKETI = 5
REFILL_MINUTA = 30
PAKETI_PO_REFILLU = 2

# Granice edicija
GRANICA_TUTTO = 239
GRANICA_SPECIALE_ZAGOR = 239 + 38 

# --- 3. INICIJALIZACIJA STANJA ---
if 'album' not in st.session_state:
    st.session_state.album = {} 
    st.session_state.paketi = POCETNI_PAKETI
    st.session_state.zadnji_refill = datetime.now()

# Logika za nove paketiće
prolo_vremena = datetime.now() - st.session_state.zadnji_refill
if prolo_vremena > timedelta(minutes=REFILL_MINUTA):
    broj_refilla = int(prolo_vremena.total_seconds() // (REFILL_MINUTA * 60))
    st.session_state.paketi += (broj_refilla * PAKETI_PO_REFILLU)
    st.session_state.zadnji_refill = datetime.now()

# --- 4. CSS ZA FIKSNI FORMAT (Da se album ne pomiče) ---
st.markdown("""
    <style>
    .slicica-okvir {
        width: 150px;
        height: 220px;
        border: 2px solid #444;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 5px;
        overflow: hidden;
        background-color: #222;
    }
    .slicica-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. FUNKCIJA ZA PRIKAZ SLIKA ---
def prikazi_slicicu(broj, kolicina=None, fali=False):
    broj_str = str(broj).zfill(3)
    
    # Putanja do tvojih slika na GitHubu (ako ih uploadaš u folder 'slike')
    lokalna_putanja = f"slike/{broj_str}.jpg"
    
    # URL s Bonelli stranice
    if broj <= GRANICA_TUTTO:
        url_weba = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--tutto_zagor_n__{broj}.jpg"
    elif broj <= GRANICA_SPECIALE_ZAGOR:
        br_spec = broj - GRANICA_TUTTO
        url_weba = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--speciale_zagor_n__{br_spec}.jpg"
    else:
        br_cico = broj - GRANICA_SPECIALE_ZAGOR
        url_weba = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--speciale_cico_n__{br_cico}.jpg"

    # HTML Prikaz s fiksnim dimenzijama
    if fali:
        st.markdown(f'<div class="slicica-okvir" style="background-color: #1a1a1a; color: #555;">Fali #{broj}</div>', unsafe_allow_html=True)
    else:
        # Ako imaš sliku na GitHubu, koristi nju, inače probaj web (iako web često blokira)
        img_src = lokalna_putanja if os.path.exists(lokalna_putanja) else url_weba
        st.markdown(f'<div class="slicica-okvir"><img src="{img_src}" class="slicica-img"></div>', unsafe_allow_html=True)
        st.caption(f"#{broj} {'(x'+str(kolicina)+')' if kolicina else ''}")

# --- 6. UI - NASLOVNA SLIKA (Smanjena i centrirana) ---
if os.path.exists('image_4540f7.jpg'):
    L, C, D = st.columns([1, 2, 1])
    with C:
        st.image('image_4540f7.jpg', use_container_width=True)
else:
    st.title("🪓 Zagor & Cico Digitalni Kolekcionar")

st.markdown("<h1 style='text-align: center; color: #e63946;'>Digitalni Album Naslovnica</h1>", unsafe_allow_html=True)

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header("👤 Tvoja Kolekcija")
    sakupljeno = len(st.session_state.album)
    st.metric("Sakupljeno", f"{sakupljeno} / {UKUPNO_SLICICA}")
    st.divider()
    st.metric("📦 Paketići", st.session_state.paketi)

# --- 8. OTVARANJE PAKETIĆA ---
if st.button("OTVORI PAKETIĆ 📦"):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)]
        st.subheader("Dobio si:")
        cols = st.columns(4)
        for i, br in enumerate(nove):
            st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
            with cols[i]:
                prikazi_slicicu(br, kolicina=st.session_state.album[br])
        st.balloons()
    else:
        st.error("Nemaš više paketića!")

# --- 9. PREGLED ALBUMA ---
st.divider()
st.header("📖 Pregled Albuma")
raspon = st.select_slider("Stranice:", options=[f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA, 20)])
start_br, end_br = map(int, raspon.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    stupac = (i - start_br) % 5
    with cols_album[stupac]:
        if i in st.session_state.album:
            prikazi_slicicu(i, kolicina=st.session_state.album[i])
        else:
            prikazi_slicicu(i, fali=True)
