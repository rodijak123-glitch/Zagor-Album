import streamlit as st
import random
import time
from datetime import datetime, timedelta
from PIL import Image
import os

# --- 1. KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="Zagor Digitalni Album",
    page_icon="🪓",
    layout="wide"
)

# --- 2. POSTAVKE ALBUMA ---
UKUPNO_SLICICA = 385
SLICICA_U_PAKETU = 4
POCETNI_PAKETI = 5
REFILL_MINUTA = 30
PAKETI_PO_REFILLU = 2
BASE_IMAGE_URL = "https://www.stripovi.com/covers/"

# --- 3. INICIJALIZACIJA STANJA (Session State) ---
if 'album' not in st.session_state:
    st.session_state.album = {}  # {broj_slicice: kolicina}
    st.session_state.paketi = POCETNI_PAKETI
    st.session_state.zadnji_refill = datetime.now()

# Logika za dodavanje novih paketića
prolo_vremena = datetime.now() - st.session_state.zadnji_refill
if prolo_vremena > timedelta(minutes=REFILL_MINUTA):
    broj_refilla = int(prolo_vremena.total_seconds() // (REFILL_MINUTA * 60))
    st.session_state.paketi += (broj_refilla * PAKETI_PO_REFILLU)
    st.session_state.zadnji_refill = datetime.now()

# --- 4. FUNKCIJE ---
def get_zagor_url(broj):
    broj_str = str(broj).zfill(3)
    return f"{BASE_IMAGE_URL}Zagor_LEX_{broj_str}.jpg"

# --- 5. UI - NASLOVNA SLIKA (SMANJENA I CENTRIRANA) ---
if os.path.exists('zagor_chico.jpg'):
    # Omjer 1:2:1 stvara srednji stupac koji je 50% širine ekrana
    L, C, D = st.columns([1, 2, 1])
    with C:
        st.image('zagor_chico.jpg', use_container_width=True)
else:
    st.title("🪓 Zagor Te-Nay: Digitalni Kolekcionar")

st.markdown("<h1 style='text-align: center; color: #e63946;'>Digitalni Album Naslovnica</h1>", unsafe_allow_html=True)

# --- 6. SIDEBAR (STATISTIKA) ---
with st.sidebar:
    st.header("👤 Tvoja Kolekcija")
    sakupljeno = len(st.session_state.album)
    procent = (sakupljeno / UKUPNO_SLICICA) * 100
    st.metric("Sakupljeno", f"{sakupljeno} / {UKUPNO_SLICICA}", f"{procent:.1f}%")
    st.divider()
    st.metric("Dostupni paketići", st.session_state.paketi)
    
    vrijeme_do = (st.session_state.zadnji_refill + timedelta(minutes=REFILL_MINUTA)) - datetime.now()
    if vrijeme_do.total_seconds() > 0:
        st.write(f"Novi paketi za: {int(vrijeme_do.total_seconds()//60)}m {int(vrijeme_do.total_seconds()%60)}s")

# --- 7. OTVARANJE PAKETIĆA ---
st.divider()
if st.button("OTVORI PAKETIĆ 📦"):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        nove = [random.randint(1, UKUPNO_SLICICA
