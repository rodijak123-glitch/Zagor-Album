import streamlit as st
import random
import os
import base64

st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 1. FUNKCIJE ---
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

# --- 3. CSS (Agresivno uklanjanje praznina) ---
bg_data = get_base64('image_50927d.jpg') #
st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    .block-container {{ padding: 10px !important; }}
    
    /* MREŽA KOJA NE DOPUŠTA VELIKE RAZMAKE */
    .album-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 15px; /* Točno definiran razmak od cca 0.5cm do 1cm */
        margin-top: 5px;
    }}
    .slot {{
        text-align: center;
        width: 150px; /* Povećano za 20% */
        margin: auto;
    }}
    .okvir {{
        width: 150px;
        height: 200px;
        background: rgba(0,0,0,0.6);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #888;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .zalijepljena {{
        width: 150px;
        height: 200px;
        object-fit: cover;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }}
    .broj {{ font-size: 12px; font-weight: bold; margin-top: 2px; color: #333; }}
    </style>
''', unsafe_allow_html=True)

# --- 4. INTERFEJS ---
st.markdown("<h2 style='text-align: center; color: #8B0000; margin: 0;'>Zagor: Digitalni Album</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Zalijepljeno", f"{len(st.session_state.album)}/458")
c2.metric("Paketići", st.session_state.paketi)
if c3.button("📦 OTVORI PAKETIĆ", use_container_width=True):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        st.session_state.na_cekanju.extend([random.randint(1, 458) for _ in range(5)])
        st.rerun()

# --- 5. LIJEPLJENJE ---
if st.session_state.na_cekanju:
    st.write("### 📥 U ruci (Klikni na broj ispod za lijepljenje):")
    cols = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with cols[i]:
            path = get_file_path(br)
            img_b64 = get_base64(path)
            if img_b64:
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" width="100">', unsafe_allow_html=True)
            if st.button(f"Zalijepi #{br}", key=f"btn_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.pop(i)
                st.rerun()

st.divider()

# --- 6. ALBUM GRID (Bez st.columns, čisti HTML/CSS) ---
options = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=options)
start, end = map(int, izabrano.split("-"))

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
