import streamlit as st
import random
import os
import base64
import time
import json
from datetime import datetime, timedelta

# --- 1. POSTAVKE I SLIKE ---
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

# --- 2. BAZA PODATAKA (JSON) ---
DB_FILE = "album_baza.json"

def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def spremi_u_bazu(baza):
    with open(DB_FILE, "w") as f: json.dump(baza, f)

baza = ucitaj_bazu()

# --- 3. IDENTIFIKACIJA ---
st.title("🛡️ Zagor: Burza Sličica")
ja = st.text_input("Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# --- 4. TRŽNICA (Tko što nudi/traži) ---
st.header("🔄 Tržnica Sličica")
tab1, tab2 = st.tabs(["Dostupne razmjene", "Moje ponude"])

with tab1:
    # Tražimo druge kolekcionare
    drugi_kolekcionari = [k for k in baza.keys() if k != ja]
    
    for drugi in drugi_kolekcionari:
        njegovi_dupli = set(baza[drugi]["duplikati"])
        meni_fale = set(range(1, 459)) - set(moj_data["album"])
        
        # Što on ima, a meni treba
        interesantno = njegovi_dupli.intersection(meni_fale)
        
        if interesantno:
            with st.expander(f"Kolekcionar {drugi} nudi: {list(interesantno)}"):
                st.write(f"Tebi fale ove sličice koje {drugi} ima duplo.")
                dajem = st.multiselect(f"Što nudiš zauzvrat iz svojih duplikata?", moj_data["duplikati"], key=f"nudi_{drugi}")
                trazim = st.multiselect(f"Koje njegove duplikate želiš?", list(interesantno), key=f"trazi_{drugi}")
                
                if st.button(f"Pošalji ponudu za {drugi}"):
                    nova_ponuda = {
                        "od": ja,
                        "nudi": dajem,
                        "trazi": trazim,
                        "status": "na_cekanju"
                    }
                    baza[drugi]["ponude"].append(nova_ponuda)
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")

with tab2:
    st.write("### 📥 Pristigle ponude:")
    for idx, p in enumerate(moj_data["ponude"]):
        if p["status"] == "na_cekanju":
            st.info(f"**{p['od']}** ti nudi {p['nudi']} za tvoje {p['trazi']}")
            c1, c2, c3 = st.columns(3)
            if c1.button("✅ Prihvati", key=f"acc_{idx}"):
                # Logika zamjene (makni/dodaj u oba albuma)
                for s in p["nudi"]: 
                    if s not in moj_data["album"]: moj_data["album"].append(s)
                for s in p["trazi"]: 
                    if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
                # Isto za drugog korisnika (treba kompleksnija logika za punu bazu)
                p["status"] = "prihvaceno"
                spremi_u_bazu(baza)
                st.rerun()
            if c2.button("❌ Odbij", key=f"rej_{idx}"):
                p["status"] = "odbijeno"
                spremi_u_bazu(baza)
                st.rerun()
            c3.write("*(Za prilagodbu, odbij i pošalji novu)*")

st.divider()

# --- 5. POZADINA I STATUS ---
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }} [data-testid="stSidebar"] {{ display: none; }} </style>', unsafe_allow_html=True)

# Gornji metri (identično kao prije)
c1, c2, c3 = st.columns(3)
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])
# Ovdje bi išao brojač...

# --- 6. ALBUM GRID (Dizajn iz image_601984.jpg) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_items = ""
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; height:200px; object-fit:cover; border-radius:10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.5);">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.8); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888; font-family:sans-serif;">Fali #{i}</div>'
    
    grid_items += f'<div style="text-align:center; padding-bottom: 20px;">{content}<div style="color:white; font-weight:bold; margin-top:10px; font-family:sans-serif; font-size:14px;">Br. {i}</div></div>'

full_html = f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 35px; justify-items:center; padding: 10px;">{grid_items}</div>'
import streamlit.components.v1 as components
components.html(full_html, height=1100, scrolling=False)
