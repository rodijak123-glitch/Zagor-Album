import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Zagor Album", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- CSS KOJI "ZAKUCAVA" DIMENZIJE ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    .main .block-container { padding: 2rem; }
    
    .album-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 38px; /* Razmak od 1cm */
        justify-items: center;
    }
    
    .slot {
        width: 150px; /* +20% veličina */
        text-align: center;
    }
    
    .okvir {
        width: 150px;
        height: 200px;
        background: #262730;
        border: 1px solid #444;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #888;
    }
    
    .zalijepljena {
        width: 150px;
        height: 200px;
        object-fit: cover;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Zagor: Digitalni Album")
st.write(f"Zalijepljeno: {len(st.session_state.album)} | Paketići: {st.session_state.paketi}")

if st.button("📦 OTVORI NOVI PAKETIĆ"):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        st.session_state.na_cekanju.extend([random.randint(1, 458) for _ in range(5)])
        st.rerun()

st.divider()

# --- NAVIGACIJA ---
stranica = st.select_slider("Stranica:", options=[f"{i}-{i+19}" for i in range(1, 459, 20)])
start, end = map(int, stranica.split("-"))

# --- KONSTRUKCIJA CIJELOG ALBUMA U JEDNOM STRINGU ---
album_html = '<div class="album-container">'

for i in range(start, min(end + 1, 459)):
    if i in st.session_state.album:
        img_data = get_base64(get_file_path(i))
        sadrzaj = f'<img src="data:image/jpeg;base64,{img_data}" class="zalijepljena">'
    else:
        sadrzaj = f'<div class="okvir">Fali #{i}</div>'
    
    album_html += f'<div class="slot">{sadrzaj}<div style="margin-top:5px">Br. {i}</div></div>'

album_html += '</div>'

# ISPIS CIJELOG BLOKA ODJEDNOM
st.markdown(album_html, unsafe_allow_html=True)
