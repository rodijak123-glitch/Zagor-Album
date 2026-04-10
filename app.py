import streamlit as st
import random
import os
import base64

# --- 1. OSNOVNA KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album", layout="wide")

# Funkcija za pretvaranje slika u format koji HTML razumije
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

# --- 2. STANJE APLIKACIJE ---
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 3. STIL (CSS) ---
# Ovdje fiksiramo razmak između redova na 1cm (cca 35px)
st.markdown(f'''
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    
    .album-mreza {{
        display: flex;
        flex-wrap: wrap;
        gap: 15px; /* Razmak između sličica */
        justify-content: center;
        margin-top: 10px;
    }}
    
    .slot {{
        width: 150px; /* Povećano za 20% od originala */
        margin-bottom: 35px; /* Razmak između redova - točno 1cm */
        text-align: center;
    }}
    
    .okvir {{
        width: 150px;
        height: 200px;
        background-color: rgba(0,0,0,0.6);
        border: 2px solid #555;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
    }}
    
    .slika-album {{
        width: 150px;
        height: 200px;
        border-radius: 10px;
        object-fit: cover;
    }}
    
    .broj-tekst {{
        font-weight: bold;
        margin-top: 5px;
    }}
    </style>
''', unsafe_allow_html=True)

# --- 4. ZAGLAVLJE ---
st.title("Zagor: Digitalni Album")
st.write(f"Zalijepljeno: {len(st.session_state.album)} / 458 | Paketića: {st.session_state.paketi}")

if st.button("📦 OTVORI NOVI PAKETIĆ"):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        st.session_state.na_cekanju.extend([random.randint(1, 458) for _ in range(5)])
        st.rerun()

# --- 5. PRIKAZ ALBUMA ---
stranica = st.select_slider("Stranica:", options=[f"{i}-{i+19}" for i in range(1, 459, 20)])
start, end = map(int, stranica.split("-"))

# POČETAK MREŽE
html_kod = '<div class="album-mreza">'

for i in range(start, min(end + 1, 459)):
    if i in st.session_state.album:
        # Ako je sličica zalijepljena
        b64 = get_base64(get_file_path(i))
        sadrzaj = f'<img src="data:image/jpeg;base64,{b64}" class="slika-album">'
    else:
        # Ako fali (tvoj HTML format)
        sadrzaj = f'<div class="okvir">Fali #{i}</div>'
    
    html_kod += f'''
        <div class="slot">
            {sadrzaj}
            <div class="broj-tekst">Br. {i}</div>
        </div>
    '''

html_kod += '</div>' # KRAJ MREŽE

st.markdown(html_kod, unsafe_allow_html=True)
