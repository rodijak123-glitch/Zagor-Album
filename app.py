import streamlit as st
import random
import os
import base64
import json
from datetime import datetime

# --- 1. KONFIGURACIJA I POZADINA ---
st.set_page_config(page_title="Zagor: Digitalni Album", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# VRAĆANJE POZADINE I STILA
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover;
        background-attachment: fixed;
    }}
    [data-testid="stMetricValue"] {{ font-size: 32px !important; color: #ff4b4b !important; }}
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

# --- 3. KORISNIK ---
st.title("🛡️ Zagor: Burza Sličica")
ja = st.text_input("Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# Sigurnosna provjera da ne pukne kôd
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data: moj_data[k] = []

# --- 4. BROJČANICI (SADA VIDLJIVI) ---
st.write("### Statistika tvog albuma")
c1, c2, c3 = st.columns([1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])

if c3.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        moj_data["u_ruci"] = random.sample(range(1, 459), 5)
        spremi_u_bazu(baza)
        st.rerun()

# --- 5. LIJEPLJENJE (VELIKE SLIKE) ---
if moj_data["u_ruci"]:
    st.write("---")
    st.subheader("📥 Nove sličice (klikni na gumb za lijepljenje):")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}"):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. TRŽNICA (FIX ZA 413) ---
st.header("🔄 Tržnica Sličica")
t1, t2 = st.tabs(["Dostupne razmjene", "Moje ponude/Sandučić"])

with t1:
    ostali = [k for k in baza.keys() if k != ja]
    for k in ostali:
        fale_meni = set(range(1, 459)) - set(moj_data["album"])
        njegovi_dupli = set(baza[k].get("duplikati", []))
        interes = njegovi_dupli.intersection(fale_meni)
        
        if interes:
            st.info(f"💡 **{k}** ima što ti treba: `{list(interes)}`")
            dajem = st.multiselect(f"Što daješ za #{list(interes)[0]}?", moj_data["duplikati"], key=f"d_{k}")
            trazim = st.multiselect(f"Što uzimaš?", list(interes), key=f"u_{k}")
            
            if st.button(f"Pošalji ponudu - {k}", key=f"b_{k}"):
                if dajem and trazim:
                    baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")

with t2:
    if not moj_data["ponude"]:
        st.write("Nemaš novih ponuda.")
    else:
        for idx, p in enumerate(list(moj_data["ponude"])):
            st.warning(f"📩 **{p['od']}** ti nudi {p['nudi']} za tvoje {p['trazi']}")
            ca, cb = st.columns(2)
            if ca.button("✅ Prihvati", key=f"acc_{idx}"):
                partner = p['od']
                # RAZMJENA I BRISANJE
                for s in p["nudi"]:
                    if s not in moj_data["album"]: moj_data["album"].append(s)
                    if s in baza[partner]["duplikati"]: baza[partner]["duplikati"].remove(s)
                for s in p["trazi"]:
                    if s not in baza[partner]["album"]: baza[partner]["album"].append(s)
                    if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
                
                moj_data["ponude"].pop(idx)
                spremi_u_bazu(baza)
                st.rerun()
            if cb.button("❌ Odbij", key=f"rej_{idx}"):
                moj_data["ponude"].pop(idx)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 7. ALBUM GRID (VRAĆENA VELIČINA) ---
st.subheader("📖 Tvoj Album")
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 20px; justify-items:center;">'
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        # Povećano na 150px širine
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; border-radius:10px; border: 2px solid #ff4b4b;">'
    else:
        content = f'<div style="width:150px; height:210px; background:rgba(255,255,255,0.1); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#aaa; font-family:sans-serif;">Fali #{i}</div>'
    grid_html += f'<div>{content}<div style="color:white; text-align:center; margin-top:5px;">Br. {i}</div></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
components.html(grid_html, height=1000)
