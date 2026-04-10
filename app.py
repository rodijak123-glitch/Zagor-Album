import streamlit as st
import random
import time
from datetime import datetime, timedelta
from PIL import Image
import os

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="Zagor Digitalni Album | Zagor Te-Nay",
    page_icon="🪓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KONFIGURACIJA ALBUMA ---
UKUPNO_SLICICA = 385
SLICICA_U_PAKETU = 4
POCETNI_PAKETI = 5
PAKETI_REFILL_KOMADA = 2
REFILL_INTERVAL_MINUTA = 30
BASE_IMAGE_URL = "https://www.stripovi.com/covers/" 

# --- INICIJALIZACIJA STANJA ---
if 'album' not in st.session_state:
    st.session_state.album = {}  
    st.session_state.paketi_na_raspolaganju = POCETNI_PAKETI
    st.session_state.zadnji_refill = datetime.now()
    st.session_state.prikazi_balloons = False

def get_zagor_image_url(broj):
    broj_str = str(broj).zfill(3)
    return f"{BASE_IMAGE_URL}Zagor_LEX_{broj_str}.jpg"

def provjeri_i_dodaj_pakete():
    trenutno_vrijeme = datetime.now()
    prolo_vremena = trenutno_vrijeme - st.session_state.zadnji_refill
    broj_intervala = int(prolo_vremena.total_seconds() // (REFILL_INTERVAL_MINUTA * 60))
    if broj_intervala > 0:
        st.session_state.paketi_na_raspolaganju += (broj_intervala * PAKETI_REFILL_KOMADA)
        st.session_state.zadnji_refill += timedelta(minutes=broj_intervala * REFILL_INTERVAL_MINUTA)

provjeri_i_dodaj_pakete()

# --- CSS STILIZACIJA (PAZI NA NAVODNIKE OVDJE) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3.5em;
        background-color: #e63946;
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .slicica-container {
        border-radius: 10px;
        padding: 5px;
        text-align: center;
        background-color: #f1faee;
        margin-bottom: 15px;
    }
    .slicica-duplikat {
        color: #e63946;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- UI - NASLOV ---
if os.path.exists('zagor_chico.jpg'):
    image_header = Image.open('zagor_chico.jpg')
    st.image(image_header, use_container_width=True)
else:
    st.title("🪓 Zagor Te-Nay: Digitalni Kolekcionar")

st.markdown("<h1 style='text-align: center; color: #e63946;'>Digitalni Album Naslovnica</h1>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("👤 Tvoja Kolekcija")
    broj_sakupljenih = len(st.session_state.album)
    procent = (broj_sakupljenih / UKUPNO_SLICICA) * 100
    st.metric("Sakupljeno", f"{broj_sakupljenih} / {UKUPNO_SLICICA}", f"{procent:.1f}%")
    st.divider()
    st.metric("Paketići", st.session_state.paketi_na_raspolaganju)

# --- OTVARANJE PAKETIĆA ---
if st.button("OTVORI PAKETIĆ 💥"):
    if st.session_state.paketi_na_raspolaganju > 0:
        st.session_state.paketi_na_raspolaganju -= 1
        nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)]
        
        st.subheader("Dobio si:")
        cols = st.columns(4)
        for i, br in enumerate(nove):
            st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
            with cols[i]:
                st.image(get_zagor_image_url(br), caption=f"#{br}")
                if st.session_state.album[br] > 1:
                    st.write("DUPLIKAT")
        st.balloons()
    else:
        st.error("Nemaš više paketića!")

# --- PRIKAZ ALBUMA ---
st.divider()
stranice = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA, 20)]
izabrana = st.select_slider("Stranica:", options=stranice)
start_br, end_br = map(int, izabrana.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols_album[(i - start_br) % 5]:
        if i in st.session_state.album:
            st.image(get_zagor_image_url(i), caption=f"#{i} (x{st.session_state.album[i]})")
        else:
            st.image(f"https://placehold.co/200x300/cccccc/999999?text={i}", caption=f"Fali #{i}")
