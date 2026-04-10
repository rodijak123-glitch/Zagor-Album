import streamlit as st
import random
import os
import base64
import time
import json
from datetime import datetime, timedelta

# --- 1. POSTAVKE ---
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
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def spremi_u_bazu(baza):
    with open(DB_FILE, "w") as f: json.dump(baza, f)

baza = ucitaj_bazu()

# --- 3. IDENTIFIKACIJA I POPRAVAK KLJUČEVA ---
st.title("🛡️ Zagor: Burza Sličica")
ja = st.text_input("Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": []}
    spremi_u_bazu(baza)

# KLJUČNO: Ako korisnik postoji, ali nema "ponude" (popravlja image_608a60.png)
if "ponude" not in baza[ja]:
    baza[ja]["ponude"] = []
    spremi_u_bazu(baza)

moj_data = baza[ja]

# --- 4. TRŽNICA ---
st.header("🔄 Tržnica Sličica")
tab1, tab2 = st.tabs(["Dostupne razmjene", "Moje ponude"])

with tab1:
    drugi_kolekcionari = [k for k in baza.keys() if k != ja]
    for drugi in drugi_kolekcionari:
        # Sigurnosna provjera za duplikate drugog korisnika
        njegovi_dupli = set(baza[drugi].get("duplikati", []))
        meni_fale = set(range(1, 459)) - set(moj_data.get("album", []))
        interesantno = njegovi_dupli.intersection(meni_fale)
        
        if interesantno:
            with st.expander(f"Kolekcionar {drugi} nudi: {list(interesantno)}"):
                dajem = st.multiselect(f"Što nudiš iz svojih duplikata?", moj_data.get("duplikati", []), key=f"n_src_{drugi}")
                trazim = st.multiselect(f"Što želiš od njega?", list(interesantno), key=f"t_src_{drugi}")
                if st.button(f"Pošalji ponudu", key=f"btn_{drugi}"):
                    if "ponude" not in baza[drugi]: baza[drugi]["ponude"] = []
                    baza[drugi]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim, "status": "na_cekanju"})
                    spremi_u_bazu(baza)
                    st.success("Poslano!")

with tab2:
    st.write("### 📥 Pristigle ponude:")
    for idx, p in enumerate(moj_data["ponude"]):
        if p.get("status") == "na_cekanju":
            st.info(f"**{p['od']}** nudi {p['nudi']} za tvoje {p['trazi']}")
            c1, c2 = st.columns(2)
            if c1.button("✅ Prihvati", key=f"acc_{idx}"):
                # Logika razmjene
                for s in p["nudi"]:
                    if s not in moj_data["album"]: moj_data["album"].append(s)
                for s in p["trazi"]:
                    if s in moj_data["duplikati"]: moj_data.get("duplikati").remove(s)
                p["status"] = "prihvaceno"
                spremi_u_bazu(baza)
                st.rerun()
            if c2.button("❌ Odbij", key=f"rej_{idx}"):
                p["status"] = "odbijeno"
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 5. POZADINA ---
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }} [data-testid="stSidebar"] {{ display: none; }} </style>', unsafe_allow_html=True)

# --- 6. ALBUM (Dizajn iz image_5fb120.png / image_601984.jpg) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_items = ""
for i in range(start, end + 1):
    if i in moj_data.get("album", []):
        path = get_file_path(i)
        img_b64 = get_base64(path)
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; height:200px; object-fit:cover; border-radius:10px;">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.8); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888;">Fali #{i}</div>'
    
    grid_items += f'<div style="text-align:center; padding-bottom:20px;">{content}<div style="color:white; font-weight:bold; margin-top:10px;">Br. {i}</div></div>'

# HTML Prikaz (Popravlja image_5fac88.png tako da NE ispisuje kôd)
import streamlit.components.v1 as components
full_html = f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 35px; justify-items:center; padding: 10px;">{grid_items}</div>'
components.html(full_html, height=1100, scrolling=False)
