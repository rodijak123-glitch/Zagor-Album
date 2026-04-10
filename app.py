import streamlit as st
import random
from datetime import datetime, timedelta
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Domaća Kolekcija", layout="wide")

# --- 2. DEFINICIJA ALBUMA ---
UKUPNO_SLICICA = 458 
SLICICA_U_PAKETU = 5
POCETNI_PAKETI = 5
REFILL_MINUTA = 30

GRANICA_EXTRA_PRVI_DIO = 75
GRANICA_EXTRA_UKUPNO = 385
GRANICA_SPECIJALI = 431 

# --- 3. FUNKCIJA ZA POZADINU ---
def set_background(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        st.markdown(f'''
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("data:image/jpeg;base64,{bin_str}");
                background-size: cover; 
                background-attachment: fixed;
            }}
            [data-testid="stSidebar"] {{ background-color: rgba(255, 255, 255, 0.5); }}
            </style>
            ''', unsafe_allow_html=True)

# Postavljanje tvoje slike kao pozadine
set_background('image_50927d.jpg') 

# --- 4. INICIJALIZACIJA STANJA ---
if 'album' not in st.session_state:
    st.session_state.album = {}
    st.session_state.paketi = POCETNI_PAKETI
    st.session_state.zadnji_refill = datetime.now()

# --- 5. LOGIKA ZA NAZIVE DATOTEKA ---
def get_file_path(broj):
    folder = "slike/"
    if broj <= GRANICA_EXTRA_PRVI_DIO:
        return f"{folder}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= GRANICA_EXTRA_UKUPNO:
        return f"{folder}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= GRANICA_SPECIJALI:
        br_spec = broj - GRANICA_EXTRA_UKUPNO
        return f"{folder}TN_ZG_LUSP_{br_spec}.jpeg"
    else:
        br_cico = broj - GRANICA_SPECIJALI
        return f"{folder}TN_ZG_LUCI_{br_cico}.jpeg"

# --- 6. STIL KARTICA ---
st.markdown("""
    <style>
    .slicica-okvir {
        width: 100%; aspect-ratio: 2/3; border: 2px solid #8B0000;
        border-radius: 8px; display: flex; align-items: center;
        justify-content: center; background-color: rgba(0,0,0,0.8);
        overflow: hidden; margin-bottom: 5px;
    }
    .slicica-img { width: 100%; height: 100%; object-fit: cover; }
    .fali-tekst { color: #888; font-size: 0.7rem; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

def prikazi_slicicu(broj, kolicina=None, fali=False):
    path = get_file_path(broj)
    if fali:
        st.markdown(f'<div class="slicica-okvir"><div class="fali-tekst">Fali #{broj}</div></div>', unsafe_allow_html=True)
    else:
        if os.path.exists(path):
            st.image(path)
        else:
            st.markdown(f'<div class="slicica-okvir"><div style="color:white;">#{broj}<br><small>Nema slike</small></div></div>', unsafe_allow_html=True)
        
        txt = f"#{broj}" + (f" (x{kolicina})" if kolicina and kolicina > 1 else "")
        st.caption(txt)

# --- 7. SIDEBAR (STATISTIKA) ---
with st.sidebar:
    st.header("👤 Tvoja Kolekcija")
    sakupljeno = len(st.session_state.album)
    st.metric("Sakupljeno", f"{sakupljeno} / {UKUPNO_SLICICA}", f"{(sakupljeno/UKUPNO_SLICICA*100):.1f}%")
    st.divider()
    st.metric("📦 Dostupni paketići", st.session_state.paketi)

# --- 8. GLAVNI NASLOV ---
st.markdown("<h1 style='text-align: center; color: #8B0000; margin-top: -50px;'>Zagor: Domaći Digitalni Album</h1>", unsafe_allow_html=True)

# --- 9. OTVARANJE PAKETIĆA ---
st.divider()
if st.button("OTVORI PAKETIĆ 📦 (5 sličica)", use_container_width=True):
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
    st.subheader("U paketiću si dobio:")
    cols = st.columns(5)
    for i, br in enumerate(st.session_state.zadnji_paket):
        with cols[i]:
            prikazi_slicicu(br)

# --- 10. PREGLED ALBUMA ---
st.divider()
st.header("📖 Pregled Albuma")
sekcija = st.radio("Edicija:", ["Sve", "Extra (1-385)", "Specijali (386-431)", "Čiko (432-458)"], horizontal=True)

if sekcija == "Extra (1-385)": r_min, r_max = 1, 385
elif sekcija == "Specijali (386-431)": r_min, r_max = 386, 431
elif sekcija == "Čiko (432-458)": r_min, r_max = 432, 458
else: r_min, r_max = 1, UKUPNO_SLICICA

raspon = st.select_slider("Stranice:", options=[f"{i}-{min(i+19, r_max)}" for i in range(r_min, r_max + 1, 20)])
start_br, end_br = map(int, raspon.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols_album[(i - start_br) % 5]:
        if i in st.session_state.album:
            prikazi_slicicu(i, kolicina=st.session_state.album[i])
        else:
            prikazi_slicicu(i, fali=True)
