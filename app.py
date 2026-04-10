import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. POZADINA I STABILNOST OKVIRA ---
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
            
            /* Onemogućuje Streamlitove defaultne razmake */
            [data-testid="stVerticalBlock"] {{ gap: 0.5rem !important; }}
            button[title="View fullscreen"] {{ display: none !important; }}

            /* FIKSNI PROPORCIONALNI OKVIR (Sprečava deformaciju) */
            .slicica-container {{
                aspect-ratio: 3 / 4; /* Standardni omjer Zagor sličica */
                width: 100%;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 5px;
            }}
            
            .caption-style {{
                text-align: center;
                font-size: 12px;
                color: #222;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            </style>
        ''', unsafe_allow_html=True)

apply_custom_styles('image_50927d.jpg') #

# --- 3. STANJE I DEFINICIJE ---
UKUPNO_SLICICA = 458
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []

def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"      #
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"   #
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg" #
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"         #

# --- 4. GLAVNI NASLOV I KONTROLE ---
st.markdown("<h1 style='text-align: center; color: #8B0000;'>Zagor: Digitalni Album</h1>", unsafe_allow_html=True)

# Otvaranje paketića (zadržano kao najjednostavnije rješenje)
if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    st.session_state.na_cekanju.extend([random.randint(1, UKUPNO_SLICICA) for _ in range(5)])

# Lijepljenje
if st.session_state.na_cekanju:
    st.write("### 📥 Sličice u ruci (Klikni za lijepljenje):")
    ruka_cols = st.columns(5)
    for idx, br in enumerate(st.session_state.na_cekanju[:10]):
        with ruka_cols[idx % 5]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=100)
            if st.button(f"Zalijepi #{br}", key=f"stick_{idx}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(idx)
                st.rerun()

st.divider()

# --- 5. PRIKAZ ALBUMA (Zbijeno i oštro) ---
options = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
izabrani = st.select_slider("Pregled stranica:", options=options)
start_br, end_br = map(int, izabrani.split("-"))

cols = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols[(i - start_br) % 5]:
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # 'use_container_width' osigurava da slika ne bude mutna
                st.image(putanja, use_container_width=True)
            else:
                st.markdown(f'<div class="slicica-container">#{i}</div>', unsafe_allow_html=True)
        else:
            # Prazno polje koje drži proporciju
            st.markdown(f'''
                <div class="slicica-container">
                    <span style="color: #888; font-size: 10px;">Fali #{i}</span>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown(f'<div class="caption-style">Br. {i}</div>', unsafe_allow_html=True)
