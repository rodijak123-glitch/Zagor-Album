import streamlit as st
import random
import time
from datetime import datetime, timedelta
from PIL import Image
import os

# --- 1. KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="Zagor & Cico Digitalni Album",
    page_icon="🪓",
    layout="wide"
)

# --- 2. POSTAVKE ALBUMA ---
# Izračun: 239 (Tutto) + 38 (Speciale Zagor) + 27 (Speciale Cico) = 304
UKUPNO_SLICICA = 304 
SLICICA_U_PAKETU = 4
POCETNI_PAKETI = 5
REFILL_MINUTA = 30
PAKETI_PO_REFILLU = 2

# Granice edicija za ispravan dohvat slika
GRANICA_TUTTO = 239
GRANICA_SPECIALE_ZAGOR = 239 + 38 # 277

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

# --- 4. FUNKCIJA ZA PRIKAZ SLIKA (TUTTO + SPECIALE + CICO) ---
def prikazi_slicicu(broj, kolicina=None, fali=False):
    broj_str = str(broj).zfill(3)
    lokalna_putanja = f"slike/{broj_str}.jpg"
    
    # 1. Izvor: GitHub 'slike' folder
    if os.path.exists(lokalna_putanja):
        st.image(lokalna_putanja, caption=f"#{broj}")
    else:
        # 2. Izvor: Bonelli (Pametno biranje edicije)
        if broj <= GRANICA_TUTTO:
            # Tutto Zagor
            url_weba = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--tutto_zagor_n__{broj}.jpg"
        elif broj <= GRANICA_SPECIALE_ZAGOR:
            # Speciale Zagor (matematika: broj - 239)
            br_spec = broj - GRANICA_TUTTO
            url_weba = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--speciale_zagor_n__{br_spec}.jpg"
        else:
            # Speciale Cico (matematika: broj - 277)
            br_cico = broj - GRANICA_SPECIALE_ZAGOR
            url_weba = f"https://shop.sergiobonelli.it/resizer/-1/-1/true/1491224855663.jpg--speciale_cico_n__{br_cico}.jpg"
        
        caption_text = f"#{broj} (x{kolicina})" if kolicina else f"#{broj}"
        
        if fali:
            st.image(f"https://placehold.co/200x300/1a1a1a/cccccc?text=ZAGOR+CICO\n#{broj}", caption=f"Fali #{broj}")
        else:
            try:
                st.image(url_weba, caption=caption_text)
            except:
                st.image(f"https://placehold.co/200x300/e63946/ffffff?text=STRIP\n#{broj}", caption=caption_text)

# --- 5. UI - NASLOVNA SLIKA ---
if os.path.exists('image_4540f7.jpg'):
    L, C, D = st.columns([1, 2, 1])
    with C:
        st.image('image_4540f7.jpg', use_container_width=True)
elif os.path.exists('zagor_chico.jpg'):
    L, C, D = st.columns([1, 2, 1])
    with C:
        st.image('zagor_chico.jpg', use_container_width=True)
else:
    st.title("🪓 Zagor & Cico: Digitalni Kolekcionar")

st.markdown("<h1 style='text-align: center; color: #e63946;'>Digitalni Album: Sve Edicije</h1>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("👤 Tvoja Kolekcija")
    sakupljeno = len(st.session_state.album)
    procent = (sakupljeno / UKUPNO_SLICICA) * 100
    st.metric("Sakupljeno", f"{sakupljeno} / {UKUPNO_SLICICA}", f"{procent:.1f}%")
    st.divider()
    st.metric("📦 Paketići", st.session_state.paketi)
    
    vrijeme_do = (st.session_state.zadnji_refill + timedelta(minutes=REFILL_MINUTA)) - datetime.now()
    if vrijeme_do.total_seconds() > 0:
        st.write(f"Novi paketi za: **{int(vrijeme_do.total_seconds()//60)}m {int(vrijeme_do.total_seconds()%60)}s**")

# --- 7. OTVARANJE PAKETIĆA ---
st.divider()
if st.button("OTVORI PAKETIĆ 📦"):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)]
        
        st.subheader("Dobio si:")
        cols_nove = st.columns(4)
        for i, br in enumerate(nove):
            st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
            with cols_nove[i]:
                prikazi_slicicu(br, kolicina=st.session_state.album[br])
                if st.session_state.album[br] > 1:
                    st.info("DUPLIKAT")
                else:
                    st.success("NOVA!")
        st.balloons()
    else:
        st.error("Nemaš više paketića!")

# --- 8. PRIKAZ ALBUMA ---
st.divider()
st.header("📖 Pregled Albuma (Tutto, Speciale, Cico)")
raspon = st.select_slider("Prelistaj stranice:", options=[f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA, 20)])
start_br, end_br = map(int, raspon.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    stupac = (i - start_br) % 5
    with cols_album[stupac]:
        if i in st.session_state.album:
            prikazi_slicicu(i, kolicina=st.session_state.album[i])
        else:
            prikazi_slicicu(i, fali=True)

st.caption("Zagor Digitalni Album | Naslovnice: Tutto, Speciale Zagor & Speciale Cico")
