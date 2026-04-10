import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA (layout wide je bitan za preglednost) ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. POZADINA I FIKSNI LAYOUT ---
def apply_custom_styles(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        
        st.markdown(f'''
            <style>
            /* Pozadina albuma */
            .stApp {{
                background-image: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url("data:image/jpeg;base64,{data}");
                background-size: cover; background-attachment: fixed;
            }}
            
            /* ONEMOGUĆAVANJE POMIČNIH ELEMENATA */
            button[title="View fullscreen"] {{ display: none !important; }}
            
            /* FIKSNA VISINA OKVIRA: Ovo sprečava bilo kakvo pomicanje redova */
            .slicica-slot {{
                min-height: 200px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                margin-bottom: 20px;
            }}
            
            /* STIL ZA PRAZNO POLJE */
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
            </style>
        ''', unsafe_allow_html=True)

apply_custom_styles('image_50927d.jpg')

# --- 3. STANJE APLIKACIJE ---
UKUPNO_SLICICA = 458
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 4. PUTANJE SLIKA (Pravilno mapiranje) ---
def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 5. SIDEBAR (Ponovno vidljiv i funkcionalan) ---
with st.sidebar:
    st.header("👤 Kolekcija")
    sakupljeno = len(st.session_state.album)
    st.metric("Zalijepljeno", f"{sakupljeno} / {UKUPNO_SLICICA}")
    st.metric("Paketići", st.session_state.paketi)
    
    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(5)]
            st.session_state.na_cekanju.extend(nove)
            st.rerun()

# --- 6. PROSTOR ZA LIJEPLJENJE ---
st.markdown("<h2 style='text-align: center; color: #8B0000;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

if st.session_state.na_cekanju:
    st.write("### 📥 Sličice u ruci:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:10]):
        with ruka_cols[i % 5]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=100)
            if st.button(f"Zalijepi #{br}", key=f"btn_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 7. PREGLED ALBUMA ---
stranice = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
izabrana_strana = st.select_slider("Stranica:", options=stranice)
start_br, end_br = map(int, izabrana_strana.split("-"))

cols = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols[(i - start_br) % 5]:
        st.markdown('<div class="slicica-slot">', unsafe_allow_html=True)
        
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Slika je sada oštra i drži svoju širinu
                st.image(putanja, width=120)
        else:
            # Prazno polje koje se ne miče
            st.markdown(f'<div class="prazno-polje">Fali #{i}</div>', unsafe_allow_html=True)
            
        st.caption(f"Br. {i}")
        st.markdown('</div>', unsafe_allow_html=True)
