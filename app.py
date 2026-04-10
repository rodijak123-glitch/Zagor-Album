import streamlit as st
import random
import os
import base64
import time
import json
from datetime import datetime, timedelta

# --- 1. OSNOVNE POSTAVKE ---
st.set_page_config(page_title="Zagor: Burza Sličica", layout="wide")

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

def spremi_u_bazu(baza):
    with open(DB_FILE, "w") as f: json.dump(baza, f)

baza = ucitaj_bazu()

# --- 3. IDENTIFIKACIJA ---
ja = st.text_input("👤 Tvoje ime:", value="Gost").strip()
if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

# Popravak ključeva za stare profile
for k in ["ponude", "paketi", "u_ruci", "duplikati"]:
    if k not in baza[ja]: baza[ja][k] = [] if isinstance(baza[ja].get(k), list) else 10

moj_data = baza[ja]

# --- 4. LOGIKA VREMENA ---
zadnje = datetime.fromisoformat(str(moj_data.get("vrijeme", datetime.now())))
preostalo = (zadnje + timedelta(minutes=30)) - datetime.now()
if preostalo.total_seconds() <= 0:
    moj_data["paketi"] = moj_data.get("paketi", 0) + 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)
    st.rerun()

# --- 5. POZADINA ---
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }} [data-testid="stSidebar"] {{ display: none; }} </style>', unsafe_allow_html=True)

# --- 6. VRH: STATISTIKA I PAKETIĆI ---
st.title("🛡️ Zagor Digitalni Album")
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])
mins, secs = divmod(int(preostalo.total_seconds()), 60)
c3.write(f"⏳ Novi za:\n**{mins:02d}:{secs:02d}**")

if c4.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0:
        moj_data["paketi"] -= 1
        nove = [random.randint(1, 458) for _ in range(5)]
        moj_data["u_ruci"].extend(nove) # SPREMAMO U RUKU, NE U ALBUM
        spremi_u_bazu(baza)
        st.rerun()

# --- 7. NOVO: PRIKAZ SLIČICA U RUCI (LIJEPLJENJE) ---
if moj_data["u_ruci"]:
    st.subheader("📥 Sličice iz paketića (klikni za lijepljenje):")
    ruka_cols = st.columns(5)
    for idx, br in enumerate(moj_data["u_ruci"][:5]): # Prikazujemo max 5 odjednom
        with ruka_cols[idx]:
            st.image(get_file_path(br), width=140)
            if st.button(f"Zalijepi #{br}", key=f"stick_{idx}_{br}"):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                    st.toast(f"#{br} je duplikat! Ide u razmjenu.")
                else:
                    moj_data["album"].append(br)
                    st.toast(f"Zalijepljena sličica #{br}!")
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()
st.divider()

# --- 8. TRŽNICA I ALBUM GRID ---
with st.expander("🔄 OTVORI TRŽNICU I RAZMJENU"):
    # (Ovdje ostaje isti kod za tržnicu kao u prošloj poruci)
    st.write("Tu su tvoje ponude i razmjene...")

# --- ALBUM GRID (Dizajn iz image_601984.jpg) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_items = ""
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; height:200px; object-fit:cover; border-radius:10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.5);">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.8); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888;">Fali #{i}</div>'
    grid_items += f'<div style="text-align:center; padding-bottom: 20px;">{content}<div style="color:white; font-weight:bold; margin-top:10px;">Br. {i}</div></div>'

import streamlit.components.v1 as components
components.html(f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 35px; justify-items:center; padding: 10px;">{grid_items}</div>', height=1100)

time.sleep(1)
st.rerun()
