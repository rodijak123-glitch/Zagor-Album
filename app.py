import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. CSS ZA SIDEBAR, POZADINU I ZBIJANJE ---
def apply_custom_styles(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        st.markdown(f'''
            <style>
            /* Pozadina cijele aplikacije */
            .stApp {{
                background-image: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url("data:image/jpeg;base64,{data}");
                background-size: cover; background-attachment: fixed;
            }}
            
            /* SUŽAVANJE SIDEBARA NA POLA (cca 200px umjesto 350px) */
            [data-testid="stSidebar"] {{
                min-width: 200px !important;
                max-width: 200px !important;
            }}

            /* UKLANJANJE RAZMAKA IZMEĐU REDOVA ALBUMA */
            [data-testid="stVerticalBlock"] {{
                gap: 0.2rem !important;
            }}
            
            /* FIKSNI KONTEJNERI ZA STABILNOST */
            .slicica-slot {{
                height: 190px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                margin-bottom: 5px;
            }}

            .prazno-polje {{
                height: 150px;
                width: 110px;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaa;
                font-size: 10px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            /* Skrivanje fullscreen gumba na slikama */
            button[title="View fullscreen"] {{ display: none !important; }}
            </style>
        ''', unsafe_allow_html=True)

apply_custom_styles('image_50927d.jpg')

# --- 3. STANJE APLIKACIJE ---
UKUPNO_SLICICA = 458
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 4. PUTANJE SLIKA ---
def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 5. SIDEBAR (SUŽENI) ---
with st.sidebar:
    st.title("👤 Info")
    sakupljeno = len(st.session_state.album)
    st.metric("Sakupljeno", f"{sakupljeno}/{UKUPNO_SLICICA}")
    st.write(f"📦 Paketići: **{st.session_state.paketi}**")
    
    if st.button("📦 OTVORI", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(5)]
            st.session_state.na_cekanju.extend(nove)
            st.rerun()

# --- 6. GLAVNI DIO ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin-top: -30px;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

# Lijepljenje (prikazujemo samo 5 sličica u ruci da ne zauzmu previše mjesta)
if st.session_state.na_cekanju:
    cols_ruka = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with cols_ruka[i]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=80)
            if st.button(f"Zalijepi {br}", key=f"s_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 7. MREŽA ALBUMA ---
stranice = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
izabrana = st.select_slider("Stranica:", options=stranice)
start, end = map(int, izabrana.split("-"))

cols = st.columns(5)
for i in range(start, end + 1):
    with cols[(i - start) % 5]:
        st.markdown('<div class="slicica-slot">', unsafe_allow_html=True)
        
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Prikaz sličice oštro i precizno
                st.image(putanja, width=110)
        else:
            # Prazno polje
            st.markdown(f'<div class="prazno-polje">#{i}</div>', unsafe_allow_html=True)
            
        st.caption(f"Br. {i}")
        st.markdown('</div>', unsafe_allow_html=True)
