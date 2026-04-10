import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. CSS ZA EKSTREMNO ZBIJANJE I POVEĆANE OKVIRE ---
def apply_custom_styles(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        st.markdown(f'''
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url("data:image/jpeg;base64,{data}");
                background-size: cover; background-attachment: fixed;
            }}
            
            /* Skrivanje sidebara u potpunosti */
            [data-testid="stSidebar"] {{ display: none; }}

            /* MINIMALNI RAZMACI IZMEĐU ELEMENATA */
            [data-testid="stVerticalBlock"] {{
                gap: 0.5rem !important; /* Ovo kontrolira globalni razmak */
            }}
            
            /* PRILAGODBA SLIDERA: Smanjujemo marginu ispod njega na ~1cm */
            .stSelectSlider {{
                margin-bottom: 35px !important;
            }}

            /* FIKSNI KONTEJNER ZA POVEĆANU SLIČICU (+20%) */
            .slicica-slot {{
                height: 235px; /* Povećana visina za veći okvir */
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                margin-bottom: 30px !important; /* Razmak između redova cca 1cm */
            }}

            .prazno-polje {{
                height: 192px; /* 160px + 20% */
                width: 144px;  /* 120px + 20% */
                background: rgba(0, 0, 0, 0.6);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaa;
                font-size: 13px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }}

            button[title="View fullscreen"] {{ display: none !important; }}
            </style>
        ''', unsafe_allow_html=True)

apply_custom_styles('image_50927d.jpg')

# --- 3. STANJE ---
UKUPNO_SLICICA = 458
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 4. TOP INTERFEJS (Umjesto sidebara) ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin-top: -50px;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 1])
with c1: st.metric("Zalijepljeno", f"{len(st.session_state.album)} / {UKUPNO_SLICICA}")
with c2: st.metric("Paketići", st.session_state.st.session_state.paketi)
with c3:
    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            st.session_state.na_cekanju.extend([random.randint(1, UKUPNO_SLICICA) for _ in range(5)])
            st.rerun()

# --- 5. LIJEPLJENJE ---
if st.session_state.na_cekanju:
    cols_ruka = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with cols_ruka[i]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=110) # Povećano i ovdje
            if st.button(f"Zalijepi {br}", key=f"s_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 6. NAVIGACIJA I ALBUM ---
stranice = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
izabrana = st.select_slider("Izaberi stranicu albuma:", options=stranice)
start, end = map(int, izabrana.split("-"))

# Prikaz 5 u redu s novim dimenzijama
cols = st.columns(5)
for i in range(start, end + 1):
    with cols[(i - start) % 5]:
        st.markdown('<div class="slicica-slot">', unsafe_allow_html=True)
        
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Povećana slika za 20% (120px * 1.2 = 144px)
                st.image(putanja, width=144)
        else:
            st.markdown(f'<div class="prazno-polje">Fali #{i}</div>', unsafe_allow_html=True)
            
        st.caption(f"Br. {i}")
        st.markdown('</div>', unsafe_allow_html=True)
