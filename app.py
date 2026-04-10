import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- FUNKCIJA ZA SLIKE ---
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

# --- STANJE APLIKACIJE ---
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- CSS (Fiksiranje razmaka na 1cm i okvira +20%) ---
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    
    /* Uklanjanje sidebara i gornjeg praznog prostora */
    [data-testid="stSidebar"] {{ display: none; }}
    .block-container {{ padding-top: 1rem !important; }}

    /* MREŽA S FIKSNIM RAZMAKOM (cca 1cm) */
    .album-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        column-gap: 20px;
        row-gap: 35px; /* Razmak između redova fiksiran na ~1cm */
        margin-top: 10px;
    }}
    
    .slot {{
        text-align: center;
        width: 150px; /* Povećano za 20% */
        margin: auto;
    }}
    
    .okvir {{
        width: 150px; /* 120px + 20% */
        height: 200px; /* 160px + 20% */
        background: rgba(0,0,0,0.7);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #aaa;
        font-size: 14px;
        border: 2px solid rgba(255,255,255,0.1);
    }}
    
    .zalijepljena {{
        width: 150px;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        box-shadow: 3px 3px 15px rgba(0,0,0,0.5);
    }}
    
    .broj {{
        font-size: 13px;
        color: #222;
        margin-top: 5px;
        font-weight: bold;
    }}
    </style>
''', unsafe_allow_html=True)

# --- STATUS I KONTROLE ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin-bottom: 0;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

col_info = st.columns([1, 1, 1])
col_info[0].metric("Zalijepljeno", f"{len(st.session_state.album)}/458")
col_info[1].metric("Paketići", st.session_state.paketi)
if col_info[2].button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        st.session_state.na_cekanju.extend([random.randint(1, 458) for _ in range(5)])
        st.rerun()

st.divider()

# --- NAVIGACIJA ---
stranice = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrana = st.select_slider("Izaberi stranicu:", options=stranice)
start, end = map(int, izabrana.split("-"))

# --- GENERIRANJE ALBUMA (Korištenje tvog HTML-a u petlji) ---
grid_html = '<div class="album-grid">'
for i in range(start, end + 1):
    if i in st.session_state.album:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" class="zalijepljena">'
    else:
        # Ovo je tvoj HTML blok prilagođen za petlju
        content = f'<div class="okvir">Fali #{i}</div>'
    
    grid_html += f'''
        <div class="slot">
            {content}
            <div class="broj">Br. {i}</div>
        </div>
    '''
grid_html += '</div>'

st.markdown(grid_html, unsafe_allow_html=True)
