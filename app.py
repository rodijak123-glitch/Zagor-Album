import streamlit as st
import random
import os
import base64
import time
from datetime import datetime, timedelta

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

# --- 2. STANJE (Logika i Vrijeme) ---
if 'album' not in st.session_state: st.session_state.album = {}
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = []
if 'paketi' not in st.session_state: st.session_state.paketi = 10
if 'zadnje_vrijeme' not in st.session_state: 
    st.session_state.zadnje_vrijeme = datetime.now()

# Izračun preostalog vremena do paketića
vrijeme_do_novih = st.session_state.zadnje_vrijeme + timedelta(minutes=30)
preostalo = vrijeme_do_novih - datetime.now()

if preostalo.total_seconds() <= 0:
    st.session_state.paketi += 2
    st.session_state.zadnje_vrijeme = datetime.now()
    st.rerun()

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

# --- 4. ZAGLAVLJE I BROJAČ ---
st.title("Zagor: Digitalni Album")

c1, c2, c3 = st.columns([1, 1, 1])
c1.metric("Zalijepljeno", f"{len(st.session_state.album)}/458")
c2.metric("Paketići", st.session_state.paketi)

# Prikaz brojača
mins, secs = divmod(int(preostalo.total_seconds()), 60)
c3.warning(f"⏳ Novi paketići za: {mins:02d}:{secs:02d}")

if st.button("📦 OTVORI PAKETIĆ", use_container_width=True):
    if st.session_state.paketi > 0:
        st.session_state.paketi -= 1
        st.session_state.na_cekanju.extend([random.randint(1, 458) for _ in range(5)])
        st.rerun()

# --- 5. LIJEPLJENJE ---
if st.session_state.na_cekanju:
    st.write("---")
    cols = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:5]):
        with cols[i]:
            st.image(get_file_path(br), width=130)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}"):
                st.session_state.album[br] = True
                st.session_state.na_cekanju.remove(br)
                st.rerun()

st.divider()

# --- 6. NAVIGACIJA I ALBUM GRID ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Izaberi stranicu:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_items = ""
for i in range(start, end + 1):
    if i in st.session_state.album:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; height:200px; object-fit:cover; border-radius:10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.5);">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.8); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888; font-family:sans-serif;">Fali #{i}</div>'
    
    grid_items += f'''
        <div style="text-align:center; padding-bottom: 20px;">
            {content}
            <div style="color:white; font-weight:bold; margin-top:10px; font-family:sans-serif; font-size:14px;">Br. {i}</div>
        </div>
    '''

full_html = f'''
    <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 35px; justify-items:center; padding: 10px;">
        {grid_items}
    </div>
'''

import streamlit.components.v1 as components
# Povećan height na 1100 kako zadnji red brojeva ne bi bio odrezan
components.html(full_html, height=1100, scrolling=False)

# Automatsko osvježavanje brojača svake minute (ili češće ako želiš sekunde)
time.sleep(1)
st.rerun()
