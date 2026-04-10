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

# TAMNA POZADINA
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
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

# --- 3. KORISNIK I SIDEBAR (BROJČANIK) ---
# Brojčanik selimo lijevo da bude uvijek fiksiran
with st.sidebar:
    st.header("📊 Stanje")
    ja = st.text_input("👤 Ime:", value="Gost").strip()
    
    if ja not in baza:
        baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
        spremi_u_bazu(baza)
    
    moj_data = baza[ja]
    # Automatski fix za 413
    moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]
    
    st.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
    st.metric("Paketići", moj_data['paketi'])
    
    if st.button("🎁 OTVORI PAKETIĆ", use_container_width=True):
        if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
            moj_data["paketi"] -= 1
            moj_data["u_ruci"] = random.sample(range(1, 459), 5)
            spremi_u_bazu(baza)
            st.rerun()

# --- 4. GLAVNI EKRAN: LIJEPLJENJE ---
st.title("🛡️ Zagor Digitalni Album")

if moj_data.get("u_ruci"):
    st.subheader("📥 Nove sličice:")
    cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with cols[i]:
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

# --- 5. TRŽNICA ---
t1, t2 = st.tabs(["🔄 Razmjena", "📩 Sandučić"])
with t1:
    for k in [kor for kor in baza.keys() if kor != ja]:
        njegovi = set(baza[k].get("duplikati", []))
        interes = njegovi.intersection(set(range(1, 459)) - set(moj_data["album"]))
        if interes:
            st.write(f"💡 **{k}** nudi: `{list(interes)}`")
            d = st.multiselect(f"Što daješ?", moj_data["duplikati"], key=f"d_{k}")
            t = st.multiselect(f"Što tražiš?", list(interes), key=f"u_{k}")
            if st.button(f"Pošalji - {k}", key=f"b_{k}"):
                if d and t:
                    baza[k]["ponude"].append({"od": ja, "nudi": d, "trazi": t})
                    spremi_u_bazu(baza)
                    st.success("Poslano!")

with t2:
    for idx, p in enumerate(list(moj_data.get("ponude", []))):
        st.warning(f"**{p['od']}** nudi {p['nudi']} za {p['trazi']}")
        if st.button("✅ Prihvati", key=f"acc_{idx}"):
            for s in p["nudi"]:
                if s not in moj_data["album"]: moj_data["album"].append(s)
                if s in baza[p['od']]["duplikati"]: baza[p['od']]["duplikati"].remove(s)
            for s in p["trazi"]:
                if s not in baza[p['od']]["album"]: baza[p['od']]["album"].append(s)
                if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
            moj_data["ponude"].pop(idx)
            spremi_u_bazu(baza)
            st.rerun()

st.divider()

# --- 6. ALBUM (15 SLIKA PO STRANICI - BEZ SCROLLA) ---
st.subheader("📖 Pregled Albuma")
# Smanjeno na 15 sličica po stranici
broj_po_stranici = 15
opcije = [f"{i}-{min(i+14, 458)}" for i in range(1, 459, broj_po_stranici)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 15px; justify-items:center; padding-bottom: 30px;">'
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:160px; border-radius:10px; border: 2px solid #ff4b4b;">'
    else:
        content = f'<div style="width:160px; height:220px; background:rgba(255,255,255,0.1); border:1px solid #444; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#555;">#{i}</div>'
    grid_html += f'<div>{content}<div style="color:white; text-align:center; margin-top:8px; font-weight:bold;">Br. {i}</div></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
# scrolling=False jer nam ne treba uz 15 slika i visinu od 800px
components.html(grid_html, height=800, scrolling=False)
