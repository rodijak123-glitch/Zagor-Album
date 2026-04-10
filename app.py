import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 1. POMOĆNE FUNKCIJE ---
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

# --- 2. STANJE ---
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 3. CSS ZA FIKSNE RAZMAKE I POVEĆANE OKVIRE ---
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    .block-container {{ padding: 10px !important; }}
    
    /* MREŽA KOJA DOZVOLJAVA SAMO 1CM RAZMAKA */
    .album-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        column-gap: 15px;
        row-gap: 25px; /* Strogo fiksiran vertikalni razmak */
        margin-top: 10px;
    }}
    
    .slot {{
        text-align: center;
        width: 150px; /* Okvir +20% */
        margin: auto;
    }}
    
    .okvir {{
        width: 150px;
        height: 200px;
        background: rgba(0,0,0,0.7);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #888;
        border: 2px solid rgba(255,255,255,0.1);
    }}
    
    .zalijepljena {{
        width: 150px;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }}
    
    .broj {{ 
        font-size: 13px; 
        font-weight: bold; 
        color: #111;
        margin-top: 2px;
    }}
    </style>
''', unsafe_allow_html=True)

# --- 4. TOP UI ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin: 0;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 1.5])
c1.metric("Zalijepljeno", f"{len(st.session_state.album)}/458")
c2.metric("Paketići", st.session_state.paketi)
if c3.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        st.session_state.na_cekanju.extend([random.randint(1, 458) for _ in range(5)])
        st.rerun()

# --- 5. LIJEPLJENJE ---
if st.session_state.na_cekanju:
    st.write("---")
    st.write("### 📥 Sličice u ruci:")
    cols = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with cols[i]:
            path = get_file_path(br)
            img_b64 = get_base64(path)
            if img_b64:
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" width="110">', unsafe_allow_html=True)
            if st.button(f"Zalijepi {br}", key=f"btn_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 6. NAVIGACIJA I MREŽA ---
options = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Izaberi stranicu:", options=options)
start, end = map(int, izabrano.split("-"))

# Generiranje HTML-a prema tvojoj strukturi
grid_html = '<div class="album-grid">'
for i in range(start, end + 1):
    if i in st.session_state.album:
        img_b64 = get_base64(get_file_path(i)) #
        content = f'<img src="data:image/jpeg;base64,{img_b64}" class="zalijepljena">'
    else:
        content = f'<div class="okvir">Fali #{i}</div>' #
    
    grid_html += f'''
        <div class="slot">
            {content}
            <div class="broj">Br. {i}</div>
        </div>
    '''
grid_html += '</div>'

st.markdown(grid_html, unsafe_allow_html=True)
