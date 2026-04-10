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
    st.session_state.album = {}      # Zalijepljene sličice
if 'na_cekanju' not in st.session_state:
    st.session_state.na_cekanju = [] # Izvučene, ne-zalijepljene
if 'paketi' not in st.session_state:
    st.session_state.paketi = 5

# --- 5. POMOĆNE FUNKCIJE ---
def get_file_path(broj):
    folder = "slike/"
    if broj <= 75: return f"{folder}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{folder}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{folder}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{folder}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("👤 Statistika")
    sakupljeno = len(st.session_state.album)
    st.metric("Zalijepljeno", f"{sakupljeno} / {UKUPNO_SLICICA}")
    st.metric("Paketići", st.session_state.paketi)
    if st.session_state.na_cekanju:
        st.warning(f"Imaš {len(st.session_state.na_cekanju)} sličica za zalijepiti!")

# --- 7. OTVARANJE PAKETIĆA ---
st.markdown("<h1 style='text-align: center; color: #8B0000;'>Zagor: Digitalni Kolekcionar</h1>", unsafe_allow_html=True)

col_centar = st.columns([1, 2, 1])[1]
with col_centar:
    if st.button("OTVORI NOVI PAKETIĆ 📦", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)]
            st.session_state.na_cekanju.extend(nove)
            st.rerun()
        else:
            st.error("Nemaš više paketića!")

# --- 8. PROSTOR ZA LIJEPLJENJE (Sličice na čekanju) ---
if st.session_state.na_cekanju:
    st.subheader("📥 Sličice u ruci (Klikni na sliku da je zalijepiš u album):")
    cols = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:10]): # Prikazujemo prvih 10 za lijepljenje
        with cols[i % 5]:
            putanja = get_file_path(br)
            if os.path.exists(putanja):
                st.image(putanja, width=120)
            if st.button(f"Zalijepi #{br}", key=f"wait_{i}_{br}"):
                st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
                st.session_state.na_cekanju.pop(i)
                st.toast(f"Sličica #{br} je zalijepljena!", icon="✅")
                time_to_scroll = (br // 20) * 20
                st.session_state.pregled_raspon = f"{max(1, time_to_scroll)}-{min(time_to_scroll+19, UKUPNO_SLICICA)}"
                st.rerun()

# --- 9. PREGLED ALBUMA ---
st.divider()
st.header("📖 Album")

# Pamćenje stranice na kojoj smo bili
options = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
if 'pregled_raspon' not in st.session_state:
    st.session_state.pregled_raspon = options[0]

izabrani_raspon = st.select_slider("Stranica:", options=options, key="slider_album", value=st.session_state.pregled_raspon)
start_br, end_br = map(int, izabrani_raspon.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols_album[(i - start_br) % 5]:
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Klik na sliku otvara "veliki prikaz" u dialogu (zumiranje)
                if st.button(f"🔍 Povećaj #{i}", key=f"zoom_{i}"):
                    @st.dialog(f"Sličica #{i}")
                    def zoom_image(p):
                        st.image(p, use_container_width=True)
                        st.write(f"Količina u albumu: {st.session_state.album[i]}")
                    zoom_image(putanja)
                
                st.image(putanja, use_container_width=True)
            else:
                st.write(f"Zalijepljeno #{i}")
        else:
            st.markdown(f'''
                <div style="height:180px; border:1px dashed #888; border-radius:5px; 
                display:flex; align-items:center; justify-content:center; color:#888; font-size:12px;">
                Fali #{i}
                </div>
            ''', unsafe_allow_html=True)
        st.caption(f"Br. {i}")
