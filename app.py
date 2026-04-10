import streamlit as st
import random
import os
import base64

# --- 1. OSNOVNE POSTAVKE ---
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

# --- 2. STANJE ---
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10

# --- 3. POZADINA I STIL ---
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    </style>
''', unsafe_allow_html=True)

# --- 4. KONTROLE ---
st.title("Zagor: Digitalni Album")
c1, c2, c3 = st.columns(3)
c1.metric("Zalijepljeno", f"{len(st.session_state.album)}/458")
c2.metric("Paketići", st.session_state.paketi)

if c3.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        st.session_state.na_cekanju.extend([random.randint(1, 458) for _ in range(5)])
        st.rerun()

# --- 5. LIJEPLJENJE (GORNJI RED) ---
if st.session_state.na_cekanju:
    st.write("### 📥 Sličice u ruci:")
    cols = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with cols[i]:
            path = get_file_path(br)
            img_b64 = get_base64(path)
            if img_b64:
                st.image(path, width=130)
            if st.button(f"Zalijepi #{br}", key=f"stick_{br}_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.remove(br)
                st.rerun()

st.divider()

# --- 6. ALBUM GRID (Izolirani HTML) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

# Konstruiramo HTML sadržaj albuma
grid_items = ""
for i in range(start, end + 1):
    if i in st.session_state.album:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; height:200px; object-fit:cover; border-radius:10px;">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.9); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888;">Fali #{i}</div>'
    
    grid_items += f'''
        <div style="text-align:center;">
            {content}
            <div style="color:white; font-weight:bold; margin-top:8px;">Br. {i}</div>
        </div>
    '''

# Finalni HTML blok sa CSS gridom
full_html = f'''
    <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 30px; justify-items:center;">
        {grid_items}
    </div>
'''

# Ključni popravak: koristimo st.components.v1.html za izolaciju
import streamlit.components.v1 as components
components.html(full_html, height=1000, scrolling=False)
