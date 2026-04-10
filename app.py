import streamlit as st
import random
import os
import base64
import json
from datetime import datetime, timedelta

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Digitalni Album", layout="wide")

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

# --- 2. BAZA PODATAKA ---
DB_FILE = "album_baza.json"
def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. PROFIL KORISNIKA ---
ja = st.text_input("👤 Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# Osiguravanje ispravnih ključeva (KeyError/TypeError fix)
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data or not isinstance(moj_data[k], list):
        moj_data[k] = []
if "paketi" not in moj_data: moj_data["paketi"] = 10

# --- 4. LOGIKA ZA PAKETIĆE ---
# Provjeravamo vrijeme samo jednom pri učitavanju, bez rerun petlje
zadnje = datetime.fromisoformat(str(moj_data.get("vrijeme", datetime.now())))
if (datetime.now() - zadnje).total_seconds() > 1800: # 30 min
    moj_data["paketi"] += 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)

# --- 5. STIL I POZADINA ---
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'''<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }}</style>''', unsafe_allow_html=True)

# --- 6. STATISTIKA I GUMB ---
st.title("🛡️ Zagor: Digitalni Album")
c1, c2, c3 = st.columns([1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])

if c3.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        novi = []
        while len(novi) < 5:
            broj = random.randint(1, 458)
            if broj not in novi: novi.append(broj)
        moj_data["u_ruci"] = novi
        spremi_u_bazu(baza)
        st.rerun() # Ovdje je rerun potreban da prikaže nove slike

# --- 7. PRIKAZ SLIČICA IZ PAKETIĆA ---
if moj_data["u_ruci"]:
    st.subheader("📥 Otvaranje paketića...")
    ruka_cols = st.columns(5)
    trenutne = list(moj_data["u_ruci"])
    for i in range(5):
        with ruka_cols[i]:
            if i < len(trenutne):
                br = trenutne[i]
                st.image(get_file_path(br), use_container_width=True)
                if st.button(f"Zalijepi #{br}", key=f"s_{i}_{br}"):
                    if br in moj_data["album"]:
                        moj_data["duplikati"].append(br)
                        st.toast(f"Duplikat #{br}")
                    else:
                        moj_data["album"].append(br)
                        st.toast(f"Zalijepljeno #{br}")
                    moj_data["u_ruci"].remove(br)
                    spremi_u_bazu(baza)
                    st.rerun() # Rerun samo nakon klika na gumb
            else:
                st.markdown('<div style="height:150px; border:1px dashed #555; border-radius:10px;"></div>', unsafe_allow_html=True)

st.divider()

# --- 8. ALBUM GRID (Dizajn iz image_601984.jpg) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_items = ""
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; border-radius:10px;">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.8); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888;">Fali #{i}</div>'
    grid_items += f'<div style="text-align:center;">{content}<div style="color:white; font-weight:bold; margin-top:5px;">Br. {i}</div></div>'

import streamlit.components.v1 as components
components.html(f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 20px; justify-items:center;">{grid_items}</div>', height=1000)

# Ovdje je bio st.rerun() koji smo UKLONILI da zaustavimo treperenje.
