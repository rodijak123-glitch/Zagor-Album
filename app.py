import streamlit as st
import random
import os
import base64
import json
from datetime import datetime, timedelta
import time

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed; color: white;
    }}
    .metric-box {{
        background: rgba(255, 75, 75, 0.3);
        padding: 20px; border-radius: 15px; border: 2px solid #ff4b4b;
        text-align: center; margin-bottom: 10px;
    }}
</style>
''', unsafe_allow_html=True)

def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 2. BAZA ---
DB_FILE = "album_baza.json"
def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}
def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. KORISNIK ---
ja = st.text_input("Tvoje ime:", value="Nike").strip()

if ja not in baza:
    baza[ja] = {
        "album": [], "duplikati": [], "paketi": 10, 
        "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": [],
        "zadnji_gratis": str(datetime.now() - timedelta(minutes=30))
    }
    spremi_u_bazu(baza)

moj_data = baza[ja]
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data: moj_data[k] = []
if "zadnji_gratis" not in moj_data:
    moj_data["zadnji_gratis"] = str(datetime.now() - timedelta(minutes=30))

moj_data["duplikati"] = [d for d in moj_data["duplikati"] if d not in moj_data["album"]]

# --- 4. BROJČANICI I LIVE TIMER ---
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    st.markdown(f'<div class="metric-box">📖 Zalijepljeno<br><span style="font-size:30px; font-weight:bold;">{len(moj_data["album"])}/458</span></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-box">📦 Paketići<br><span style="font-size:30px; font-weight:bold;">{moj_data["paketi"]}</span></div>', unsafe_allow_html=True)

with col3:
    timer_placeholder = st.empty() # Spremnik za timer koji se vrti
    
    # Logika koja se vrti dok vrijeme ne istekne
    while True:
        sad = datetime.now()
        zadnje = datetime.fromisoformat(moj_data["zadnji_gratis"])
        razlika = sad - zadnje
        sekundi_ostalo = int(max(0, 1800 - razlika.total_seconds()))

        if sekundi_ostalo > 0:
            minuta = sekundi_ostalo // 60
            sekundi = sekundi_ostalo % 60
            timer_placeholder.button(f"⏳ Novi paketi za {minuta:02d}:{sekundi:02d}", disabled=True, use_container_width=True, key="timer_btn")
            time.sleep(1)
        else:
            # Kad istekne vrijeme, makni timer i prikaži gumb za preuzimanje
            timer_placeholder.empty()
            if st.button("🎁 PREUZMI 2 GRATIS PAKETA", use_container_width=True, key="gratis_btn"):
                moj_data["paketi"] += 2
                moj_data["zadnji_gratis"] = str(datetime.now())
                spremi_u_bazu(baza)
                st.rerun()
            break # Izađi iz petlje kad se prikaže gumb

    if st.button("📦 OTVORI PAKETIĆ IZ ZALIHE", use_container_width=True):
        if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
            moj_data["paketi"] -= 1
            moj_data["u_ruci"] = random.sample(range(1, 459), 5)
            spremi_u_bazu(baza)
            st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data["u_ruci"]:
    st.write("---")
    cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}"):
                if br in moj_data["album"]:
                    if br not in moj_data["duplikati"]: moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. ALBUM GRID (Dovoljna visina da nema rezanja) ---
st.subheader("📖 Tvoj Album")
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 20px; justify-items:center;">'
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:160px; border-radius:10px; border: 2px solid #ff4b4b;">'
    else:
        content = f'<div style="width:160px; height:220px; background:rgba(0,0,0,0.5); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888;">#{i}</div>'
    grid_html += f'<div>{content}<div style="color:white; text-align:center; margin-top:5px; font-weight:bold;">Br. {i}</div></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
# Visina 1150px je optimalna da se vide 4 puna reda i brojevi ispod njih
components.html(grid_html, height=1150)
