import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. CSS ZA EKSTREMNO ZBIJANJE I UKLANJANJE SIDEBARA ---
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
            
            /* POTPUNO SKRIVANJE SIDEBARA AKO JE OSTALA PRAZNINA */
            [data-testid="stSidebar"] {{ display: none; }}
            [data-testid="stSidebarNav"] {{ display: none; }}

            /* UKLANJANJE SVIH RAZMAKA IZMEĐU BLOKOVA */
            [data-testid="stVerticalBlock"] {{
                gap: 0rem !important;
                padding-top: 0rem !important;
            }}
            
            /* FIKSNI KONTEJNER ZA SLIČICU */
            .slicica-slot {{
                height: 200px; 
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                margin: 0px !important;
                padding: 0px !important;
            }}

            .prazno-polje {{
                height: 160px;
                width: 120px;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #888;
                font-size: 11px;
                border: 1px solid rgba(255,255,255,0.1);
            }}

            /* Uklanjanje kontrola za sliku */
            button[title="View fullscreen"] {{ display: none !important; }}
            </style>
        ''', unsafe_allow_html=True)

apply_custom_styles('image_50927d.jpg')

# --- 3. STANJE APLIKACIJE ---
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

# --- 4. ZAGLAVLJE (Sve što je bilo u sidebaru) ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin-top: -50px;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

# Statusna traka umjesto sidebara
info_c1, info_c2, info_c3 = st.columns([1, 1, 1])
with info_c1:
    st.metric("Zalijepljeno", f"{len(st.session_state.album)} / {UKUPNO_SLICICA}")
with info_c2:
    st.metric("Preostalo paketića", st.session_state.paketi)
with info_c3:
    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            st.session_state.na_cekanju.extend([random.randint(1, UKUPNO_SLICICA) for _ in range(5)])
            st.rerun()

# --- 5. LIJEPLJENJE ---
if st.session_state.na_cekanju:
    st.write("### 📥 Sličice u ruci:")
    cols_ruka = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with cols_ruka[i]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=90)
            if st.button(f"Zalijepi {br}", key=f"stick_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 6. MREŽA ALBUMA (Vraćeno na 5 u redu jer sada imamo punu širinu) ---
stranice = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
izabrana = st.select_slider("Stranica:", options=stranice)
start, end = map(int, izabrana.split("-"))

# Prikaz 5 u redu
cols = st.columns(5)
for i in range(start, end + 1):
    with cols[(i - start) % 5]:
        st.markdown('<div class="slicica-slot">', unsafe_allow_html=True)
        
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Slika punog kvaliteta
                st.image(putanja, width=120)
        else:
            # Fiksno prazno polje
            st.markdown(f'<div class="prazno-polje">Fali #{i}</div>', unsafe_allow_html=True)
            
        st.caption(f"Br. {i}")
        st.markdown('</div>', unsafe_allow_html=True)
