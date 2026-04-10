import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. POZADINA I FIKSNI DIZAJN ---
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
            
            /* USKI SIDEBAR */
            [data-testid="stSidebar"] {{
                min-width: 180px !important;
                max-width: 180px !important;
            }}

            /* FIKSNA VISINA ZA 4 U REDU */
            .slicica-slot {{
                height: 240px; 
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                margin-bottom: 5px;
            }}

            .prazno-polje {{
                height: 180px; /* Veći okviri za bolju vidljivost */
                width: 135px;
                background: rgba(0, 0, 0, 0.6);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #888;
                font-size: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}

            button[title="View fullscreen"] {{ display: none !important; }}
            </style>
        ''', unsafe_allow_html=True)

apply_custom_styles('image_50927d.jpg') #

# --- 3. STANJE APLIKACIJE ---
UKUPNO_SLICICA = 458
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 4. PUTANJE ---
def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 5. SIDEBAR (VRAĆEN BROJAČ I GUMB) ---
with st.sidebar:
    st.header("👤 Status")
    sakupljeno = len(st.session_state.album)
    st.metric("Zalijepljeno", f"{sakupljeno}/{UKUPNO_SLICICA}")
    
    # Brojač paketića ponovno tu
    st.write(f"📦 Preostalo paketića: **{st.session_state.paketi}**")
    
    if st.button("📦 OTVORI NOVI", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            nove = [random.randint(1, UKUPNO_SLICICA) for _ in range(5)]
            st.session_state.na_cekanju.extend(nove)
            st.rerun()

# --- 6. LIJEPLJENJE ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin-top: -30px;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

if st.session_state.na_cekanju:
    st.write("### 📥 Sličice u ruci:")
    ruka_cols = st.columns(4) # I ovdje na 4 radi konzistentnosti
    for i, br in enumerate(st.session_state.na_cekanju[:4]):
        with ruka_cols[i]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=110)
            if st.button(f"Zalijepi {br}", key=f"stick_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 7. MREŽA ALBUMA (4 U REDU) ---
stranice = [f"{i}-{min(i+15, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 16)]
izabrana = st.select_slider("Stranica:", options=stranice)
start, end = map(int, izabrana.split("-"))

cols = st.columns(4) # 4 u redu za maksimalnu oštrinu
for i in range(start, end + 1):
    with cols[(i - start) % 4]:
        st.markdown('<div class="slicica-slot">', unsafe_allow_html=True)
        
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Slika je sada veća i oštrija
                st.image(putanja, width=135)
        else:
            # Prazno polje koje se ne miče
            st.markdown(f'<div class="prazno-polje">Fali #{i}</div>', unsafe_allow_html=True)
            
        st.caption(f"Br. {i}")
        st.markdown('</div>', unsafe_allow_html=True)
