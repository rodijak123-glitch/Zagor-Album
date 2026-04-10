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

# POZADINA
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    /* Stil za brojčanike da budu veliki i uočljivi */
    .stat-text {{
        font-size: 28px; font-weight: bold; color: #ff4b4b; text-align: center;
        background: rgba(0,0,0,0.4); padding: 10px; border-radius: 10px; border: 1px solid #ff4b4b;
    }}
</style>
''', unsafe_allow_html=True)

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

def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. KORISNIK I ČIŠĆENJE ---
ja = st.text_input("Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data: moj_data[k] = []

# Trajno uklanjanje duplikata koji su već u albumu (Riješen 413)
moj_data["duplikati"] = [d for d in moj_data["duplikati"] if d not in moj_data["album"]]

# --- 4. STATISTIKA (SADA MORA BITI VIDLJIVA) ---
st.write("") # Malo razmaka od vrha
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    st.markdown(f'<div class="stat-text">📖 {len(moj_data["album"])}/458</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-text">📦 {moj_data["paketi"]} kom.</div>', unsafe_allow_html=True)
with c3:
    if st.button("📦 OTVORI PAKETIĆ", use_container_width=True):
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

# --- 6. TRŽNICA ---
t_raz, t_sand = st.tabs(["Dostupne razmjene", "Sandučić"])
with t_raz:
    ostali = [k for k in baza.keys() if k != ja]
    for k in ostali:
        njegovi_dupli = set(baza[k].get("duplikati", []))
        fale_meni = set(range(1, 459)) - set(moj_data["album"])
        interes = njegovi_dupli.intersection(fale_meni)
        if interes:
            st.info(f"💡 **{k}** nudi: `{list(interes)}`")
            dajem = st.multiselect(f"Što nudiš za #{list(interes)[0]}?", moj_data["duplikati"], key=f"d_{k}")
            trazim = st.multiselect(f"Što želiš uzeti?", list(interes), key=f"u_{k}")
            if st.button(f"Pošalji ponudu igraču {k}", key=f"b_{k}"):
                if dajem and trazim:
                    baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")

with t_sand:
    if not moj_data["ponude"]: st.write("Nemaš novih ponuda.")
    for idx, p in enumerate(list(moj_data["ponude"])):
        st.warning(f"📩 **{p['od']}** nudi {p['nudi']} za {p['trazi']}")
        if st.button("✅ Prihvati", key=f"acc_{idx}"):
            partner = p['od']
            for s in p["nudi"]:
                if s not in moj_data["album"]: moj_data["album"].append(s)
                if s in baza[partner]["duplikati"]: baza[partner]["duplikati"].remove(s)
            for s in p["trazi"]:
                if s not in baza[partner]["album"]: baza[partner]["album"].append(s)
                if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
            moj_data["ponude"].pop(idx)
            spremi_u_bazu(baza)
            st.rerun()

st.divider()

# --- 7. ALBUM GRID (FIX ZA PROSTOR I REZANJE) ---
st.subheader("📖 Tvoj Album")
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

# Povećan padding-bottom samo za elemente unutar HTML-a
grid_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 15px; justify-items:center; padding-bottom: 30px;">'
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:145px; border-radius:8px; border: 2px solid #ff4b4b;">'
    else:
        content = f'<div style="width:145px; height:200px; background:rgba(255,255,255,0.1); border:1px solid #444; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#666;">#{i}</div>'
    grid_html += f'<div>{content}<div style="color:white; text-align:center; margin-top:3px; font-size:13px;">Br. {i}</div></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
# Visina smanjena na 850 kako ne bi bilo previše praznog prostora
components.html(grid_html, height=850)
