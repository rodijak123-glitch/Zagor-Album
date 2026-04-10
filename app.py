import streamlit as st
import random
import os
import base64
import json
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# POZADINA (Smanjen intenzitet da tekst bude čitljiv)
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    .metric-box {{
        background: rgba(255, 75, 75, 0.2);
        padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b;
        text-align: center; color: white;
    }}
    /* Stil za prazan okvir koji se ne deformira */
    .empty-slot {{
        width: 100%; height: 220px; background: rgba(255,255,255,0.05);
        border: 2px dashed #444; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        color: #666; font-weight: bold; font-size: 20px;
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
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. BROJČANICI ---
st.write("---")
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    st.markdown(f'<div class="metric-box">📖 Zalijepljeno<br><span style="font-size:24px;">{len(moj_data["album"])}/458</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box">📦 Paketići<br><span style="font-size:24px;">{moj_data["paketi"]}</span></div>', unsafe_allow_html=True)
with c3:
    if st.button("🎁 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
            moj_data["paketi"] -= 1
            moj_data["u_ruci"] = random.sample(range(1, 459), 5)
            spremi_u_bazu(baza)
            st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data.get("u_ruci"):
    st.write("### 📥 Sličice u ruci:")
    cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"stick_{br}_{i}", use_container_width=True):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. ALBUM GRID (IZMJENA: SIGURNI PRIKAZ) ---
st.subheader("📖 Tvoj Album")
opcije = [f"{i}-{min(i+14, 458)}" for i in range(1, 459, 15)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

# Prikazujemo 3 reda po 5 sličica koristeći čisti Streamlit
for r in range(3):
    cols = st.columns(5)
    for c in range(5):
        br = start + (r * 5) + c
        if br <= end:
            with cols[c]:
                if br in moj_data["album"]:
                    # Sličica koja je zalijepljena
                    st.image(get_file_path(br), use_container_width=True)
                    st.markdown(f"<p style='text-align:center; color:white;'>Br. {br}</p>", unsafe_allow_html=True)
                else:
                    # Izmjena 2: Okvir koji drži visinu i ne deformira se
                    st.markdown(f'<div class="empty-slot">#{br}</div>', unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center; color:#555;'>Fali</p>", unsafe_allow_html=True)
