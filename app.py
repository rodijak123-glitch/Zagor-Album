import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. POZADINA I STROGI CSS ZA REDOVE ---
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
            
            /* FIKSIRANJE VISINE: Ovo sprečava micanje redova kad se slika pojavi */
            .slicica-slot {{
                min-height: 220px; 
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                margin-bottom: 10px;
            }}

            /* PRAZNI OKVIRI: Vraćeni na stabilnu veličinu */
            .prazno-polje {{
                height: 160px;
                width: 120px;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #999;
                font-size: 11px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            /* Skrivanje Streamlitovih kontrola */
            button[title="View fullscreen"] {{ display: none !important; }}
            </style>
        ''', unsafe_allow_html=True)

apply_custom_styles('image_50927d.jpg')

# --- 3. STANJE ---
UKUPNO_SLICICA = 458
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 4. MAPIRANJE SLIKA ---
def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 5. SIDEBAR (Lijeva strana je sada fiksna) ---
with st.sidebar:
    st.header("👤 Kolekcija")
    sakupljeno = len(st.session_state.album)
    st.metric("Zalijepljeno", f"{sakupljeno} / {UKUPNO_SLICICA}")
    st.metric("Paketići", st.session_state.paketi)
    
    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            st.session_state.na_cekanju.extend([random.randint(1, UKUPNO_SLICICA) for _ in range(5)])
            st.rerun()

# --- 6. GLAVNI EKRAN ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin-top: -20px;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

# Lijepljenje sličica iz ruke
if st.session_state.na_cekanju:
    st.write("### 📥 Sličice u ruci:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with ruka_cols[i]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=100)
            if st.button(f"Zalijepi #{br}", key=f"stick_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 7. PRIKAZ MREŽE ALBUMA ---
stranice = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
izabrana = st.select_slider("Navigacija po stranicama:", options=stranice)
start, end = map(int, izabrana.split("-"))

# Prikaz 5 sličica u redu
cols = st.columns(5)
for i in range(start, end + 1):
    with cols[(i - start) % 5]:
        st.markdown('<div class="slicica-slot">', unsafe_allow_html=True)
        
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Oštra slika, fiksna širina
                st.image(putanja, width=120)
        else:
            # Polje koje drži stabilnu visinu
            st.markdown(f'<div class="prazno-polje">Fali #{i}</div>', unsafe_allow_html=True)
            
        st.caption(f"Br. {i}")
        st.markdown('</div>', unsafe_allow_html=True)
