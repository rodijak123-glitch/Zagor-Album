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
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

# Postavi pozadinu
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
        background-color: rgba(0,0,0,0.7);
        overflow: hidden;
        margin-bottom: 5px;
    }
    .slicica-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .fali-tekst {
        color: #666;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 6. FUNKCIJA ZA PRIKAZ ---
def prikazi_slicicu(broj, kolicina=None, fali=False):
    broj_str = str(broj).zfill(3)
    
    # URL-ovi s Bonellija
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
        st.caption(f"#{broj} {'(x'+str(kolicina)+')' if kolicina else ''}")

# --- 7. NASLOVNA SLIKA ---
L, C, R = st.columns([1, 2, 1])
with C:
    if os.path.exists('image_4540f7.jpg'):
        st.image('image_4540f7.jpg', use_container_width=True)
    else:
        st.title("🪓 Zagor & Cico Album")

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
                prikazi_slicicu(br)
        st.balloons()

# --- 9. ALBUM ---
st.divider()
raspon = st.select_slider("Prelistaj stranice:", options=[f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA, 20)])
start_br, end_br = map(int, raspon.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols_album[(i - start_br) % 5]:
        if i in st.session_state.album:
            prikazi_slicicu(i, kolicina=st.session_state.album[i])
        else:
            prikazi_slicicu(i, fali=True)
