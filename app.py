import streamlit as st
import random
from datetime import datetime
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. DEFINICIJA ---
UKUPNO_SLICICA = 458 
SLICICA_U_PAKETU = 5

# --- 3. POZADINA ---
def set_background(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        st.markdown(f'''
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("data:image/jpeg;base64,{bin_str}");
                background-size: cover; background-attachment: fixed;
            }}
            </style>
            ''', unsafe_allow_html=True)

set_background('image_50927d.jpg')

# --- 4. STANJE APLIKACIJE ---
if 'album' not in st.session_state:
    st.session_state.album = {}      
if 'na_cekanju' not in st.session_state:
    st.session_state.na_cekanju = [] 
if 'paketi' not in st.session_state:
    st.session_state.paketi = 5

# --- 5. POMOĆNE FUNKCIJE ---
def get_file_path(broj):
    folder = "slike/"
    if broj <= 75: 
        return f"{folder}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: 
        return f"{folder}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: 
        # 386 postaje LUSP_1
        return f"{folder}TN_ZG_LUSP_{broj-385}.jpeg"
    else: 
        # 432 postaje LUCI_1
        return f"{folder}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("👤 Statistika")
    sakupljeno = len(st.session_state.album)
    st.metric("Zalijepljeno", f"{sakupljeno} / {UKUPNO_SLICICA}")
    st.metric("Paketići", st.session_state.paketi)
    if st.session_state.na_cekanju:
        st.warning(f"Imaš {len(st.session_state.na_cekanju)} sličica u ruci!")

# --- 7. NASLOV I OTVARANJE ---
st.markdown("<h1 style='text-align: center; color: #8B0000;'>Zagor: Digitalni Kolekcionar</h1>", unsafe_allow_html=True)

col_btn = st.columns([1, 2, 1])[1]
with col_btn:
    if st.button("OTVORI NOVI PAKETIĆ 📦", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)]
            st.session_state.na_cekanju.extend(nove)
            st.rerun()

# --- 8. LIJEPLJENJE ---
if st.session_state.na_cekanju:
    st.subheader("📥 Klikni na sličicu da je zalijepiš:")
    cols = st.columns(5)
    # Koristimo kopiju liste za iteraciju da izbjegnemo greške pri pop-u
    za_prikaz = list(enumerate(st.session_state.na_cekanju))[:10]
    
    for i, br in za_prikaz:
        with cols[i % 5]:
            putanja = get_file_path(br)
            if os.path.exists(putanja):
                st.image(putanja, width=120)
            else:
                st.write(f"Sličica #{br}")
                
            if st.button(f"Zalijepi #{br}", key=f"btn_stick_{i}_{br}"):
                # Zalijepi
                st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
                st.session_state.na_cekanju.pop(i)
                
                # Izračunaj točan raspon za slider
                start_page = ((br - 1) // 20) * 20 + 1
                end_page = min(start_page + 19, UKUPNO_SLICICA)
                st.session_state.pregled_raspon = f"{start_page}-{end_page}"
                
                st.rerun()

# --- 9. PREGLED ALBUMA ---
st.divider()
st.header("📖 Album")

# Generiraj opcije slidera (uvijek fiksne)
options = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]

# Provjera valjanosti pregled_raspon stanja
if 'pregled_raspon' not in st.session_state or st.session_state.pregled_raspon not in options:
    st.session_state.pregled_raspon = options[0]

izabrani_raspon = st.select_slider(
    "Stranica:", 
    options=options, 
    value=st.session_state.pregled_raspon,
    key="glavni_slider"
)

# Ažuriraj stanje ako korisnik ručno pomakne slider
st.session_state.pregled_raspon = izabrani_raspon

start_br, end_br = map(int, izabrani_raspon.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols_album[(i - start_br) % 5]:
        if i in st.session_state.album:
            putanja = get_file_path(i)
            # Zumiranje
            if st.button(f"🔍 Povećaj #{i}", key=f"zoom_{i}"):
                @st.dialog(f"Sličica #{i}")
                def zoom_image(p):
                    st.image(p, use_container_width=True)
                    st.write(f"Količina: {st.session_state.album[i]}")
                zoom_image(putanja)
            
            if os.path.exists(putanja):
                st.image(putanja, use_container_width=True)
            else:
                st.info(f"Slika #{i}")
        else:
            st.markdown(f'''
                <div style="height:150px; border:1px dashed #888; border-radius:5px; 
                display:flex; align-items:center; justify-content:center; color:#888; font-size:12px; background: rgba(0,0,0,0.05);">
                Fali #{i}
                </div>
            ''', unsafe_allow_html=True)
        st.caption(f"Br. {i}")
