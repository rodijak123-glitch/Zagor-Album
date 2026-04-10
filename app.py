import streamlit as st
import random
import time
from datetime import datetime, timedelta
import os
import base64

# --- 1. KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="Zagor & Cico Digitalni Album",
    page_icon="🪓",
    layout="wide"
)

# --- 2. FUNKCIJA ZA POZADINU (image_50927d.jpg) ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    if os.path.exists(png_file):
        bin_str = get_base64(png_file)
        # linear-gradient stvara efekt "posvjetljivanja" (0.85 prozirnost bijele boje)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.5);
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

# Aktiviraj pozadinu
set_background('image_50927d.jpg')

# --- 3. POSTAVKE ALBUMA ---
UKUPNO_SLICICA = 304 
SLICICA_U_PAKETU = 4
POCETNI_PAKETI = 5
REFILL_MINUTA = 30

GRANICA_TUTTO = 239
GRANICA_SPECIALE_ZAGOR = 277 

# --- 4. INICIJALIZACIJA STANJA ---
if 'album' not in st.session_state:
    st.session_state.album = {} 
    st.session_state.paketi = POCETNI_PAKETI
    st.session_state.zadnji_refill = datetime.now()

# Logika za nove paketiće
prolo_vremena = datetime.now() - st.session_state.zadnji_refill
if prolo_vremena > timedelta(minutes=REFILL_MINUTA):
    broj_refilla = int(prolo_vremena.total_seconds() // (REFILL_MINUTA * 60))
    st.session_state.paketi += (broj_refilla * 2) # Dodaje 2 paketića
    st.session_state.zadnji_refill = datetime.now()

# --- 5. STIL ZA KARTICE (CSS) ---
st.markdown("""
    <style>
    .slicica-okvir {
        width: 100%;
        aspect-ratio: 2/3;
        border: 2px solid #8B0000;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: rgba(0,0,0,0.8);
        overflow: hidden;
        margin-bottom: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .slicica-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .fali-tekst {
        color: #888;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 6. FUNKCIJA ZA PRIKAZ ---
def prikazi_slicicu(broj, kolicina=None, fali=False):
    if broj <= GRANICA_TUTTO:
        url = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--tutto_zagor_n__{broj}.jpg"
    elif broj <= GRANICA_SPECIALE_ZAGOR:
        br_spec = broj - GRANICA_TUTTO
        url = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--speciale_zagor_n__{br_spec}.jpg"
    else:
        br_cico = broj - GRANICA_SPECIALE_ZAGOR
        url = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--speciale_cico_n__{br_cico}.jpg"

    if fali:
        st.markdown(f'<div class="slicica-okvir"><div class="fali-tekst">Fali #{broj}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="slicica-okvir"><img src="{url}" class="slicica-img"></div>', unsafe_allow_html=True)
        text = f"#{broj}" + (f" (x{kolicina})" if kolicina and kolicina > 1 else "")
        st.caption(text)

# --- 7. SIDEBAR (STATISTIKA) ---
with st.sidebar:
    st.header("👤 Tvoja Kolekcija")
    sakupljeno = len(st.session_state.album)
    procent = (sakupljeno / UKUPNO_SLICICA) * 100
    st.metric("Sakupljeno", f"{sakupljeno} / {UKUPNO_SLICICA}", f"{procent:.1f}%")
    st.divider()
    st.metric("📦 Dostupni paketići", st.session_state.paketi)
    
    vrijeme_do = (st.session_state.zadnji_refill + timedelta(minutes=REFILL_MINUTA)) - datetime.now()
    if vrijeme_do.total_seconds() > 0:
        st.write(f"Novi paketi za: **{int(vrijeme_do.total_seconds()//60)}m {int(vrijeme_do.total_seconds()%60)}s**")

# --- 8. NASLOVNA SLIKA ---
L, C, R = st.columns([1, 2, 1])
with C:
    # Provjera oba moguća imena za naslovnicu
    if os.path.exists('image_4540f7.jpg'):
        st.image('image_4540f7.jpg', use_container_width=True)
    elif os.path.exists('image_45b87f.jpg'):
        st.image('image_45b87f.jpg', use_container_width=True)
    
st.markdown("<h1 style='text-align: center; color: #8B0000;'>Digitalni Album Naslovnica</h1>", unsafe_allow_html=True)

# --- 9. OTVARANJE PAKETIĆA ---
st.divider()
col_btn, col_info = st.columns([1, 3])
with col_btn:
    if st.button("OTVORI PAKETIĆ 📦", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)]
            st.session_state.zadnji_paket = nove
            for br in nove:
                st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
            st.balloons()
        else:
            st.error("Nemaš više paketića!")

if 'zadnji_paket' in st.session_state:
    st.subheader("Dobio si:")
    cols = st.columns(4)
    for i, br in enumerate(st.session_state.zadnji_paket):
        with cols[i]:
            prikazi_slicicu(br)

# --- 10. PREGLED ALBUMA ---
st.divider()
st.header("📖 Pregled Albuma")
raspon = st.select_slider("Stranice:", options=[f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA, 20)])
start_br, end_br = map(int, raspon.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols_album[(i - start_br) % 5]:
        if i in st.session_state.album:
            prikazi_slicicu(i, kolicina=st.session_state.album[i])
        else:
            prikazi_slicicu(i, fali=True)
