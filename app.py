import streamlit as st
import random
import os
import base64

# --- 1. POSTAVKE ---
st.set_page_config(page_title="Zagor Album", layout="wide")

# Funkcija za slike (za pozadinu i albume)
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

# --- 2. STANJE (Logika koja mora raditi) ---
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 3. CSS (Pozadina + Okviri iz image_5fb120.png) ---
bg_data = get_base64('image_50927d.jpg')
bg_style = ""
if bg_data:
    bg_style = f'background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/jpeg;base64,{bg_data}");'

st.markdown(f'''
    <style>
    .stApp {{
        {bg_style}
        background-size: cover;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    
    .album-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        column-gap: 20px;
        row-gap: 30px;
        justify-items: center;
        margin-top: 20px;
    }}
    
    .slot {{
        width: 155px;
        text-align: center;
    }}
    
    .okvir {{
        width: 155px;
        height: 210px;
        background: rgba(30, 30, 30, 0.8);
        border: 1px solid #444;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #888;
        font-size: 14px;
    }}
    
    .zalijepljena {{
        width: 155px;
        height: 210px;
        object-fit: cover;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }}
    
    .broj-label {{
        margin-top: 8px;
        font-weight: bold;
        color: white;
    }}
    </style>
''', unsafe_allow_html=True)

# --- 4. UI KONTROLE (Paketići i status) ---
st.title("Zagor: Digitalni Album")

c1, c2, c3 = st.columns([1, 1, 1])
with c1: st.metric("Zalijepljeno", f"{len(st.session_state.album)}/458")
with c2: st.metric("Preostalo paketića", st.session_state.paketi)
with c3:
    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            # Generiraj 5 sličica
            nove = [random.randint(1, 458) for _ in range(5)]
            st.session_state.na_cekanju.extend(nove)
            st.rerun()

# Lijepljenje sličica koje su "u ruci"
if st.session_state.na_cekanju:
    st.subheader("📥 Sličice u ruci (klikni za lijepljenje):")
    ruka_cols = st.columns(5)
    # Prikazujemo prvih 5 iz ruku
    za_prikaz = st.session_state.na_cekanju[:5]
    for idx, br in enumerate(za_prikaz):
        with ruka_cols[idx]:
            img_path = get_file_path(br)
            img_b64 = get_base64(img_path)
            if img_b64:
                st.markdown(f'<img src="data:image/jpeg;base64,{img_b64}" width="100" style="border-radius:5px">', unsafe_allow_html=True)
            if st.button(f"Zalijepi #{br}", key=f"stick_{idx}_{br}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.remove(br)
                st.rerun()

st.divider()

# --- 5. NAVIGACIJA I MREŽA ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrana_str = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrana_str.split("-"))

# Generiranje mreže
html_mreza = '<div class="album-grid">'
for i in range(start, end + 1):
    if i in st.session_state.album:
        img_b64 = get_base64(get_file_path(i))
        sadrzaj = f'<img src="data:image/jpeg;base64,{img_b64}" class="zalijepljena">'
    else:
        sadrzaj = f'<div class="okvir">Fali #{i}</div>'
    
    html_mreza += f'''
        <div class="slot">
            {sadrzaj}
            <div class="broj-label">Br. {i}</div>
        </div>
    '''
html_mreza += '</div>'

st.markdown(html_mreza, unsafe_allow_html=True)
