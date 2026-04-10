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

# VRAĆANJE POZADINE
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'''<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }}</style>''', unsafe_allow_html=True)

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
st.title("🛡️ Zagor: Digitalni Album")
ja = st.text_input("👤 Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# Sigurnosna provjera ključeva
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data: moj_data[k] = []

# --- 4. BROJČANICI (Metric) ---
# Vraćeni na vrh stranice
c1, c2, c3 = st.columns([1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])

if c3.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        novi = random.sample(range(1, 459), 5) # Garantirano 5 različitih
        moj_data["u_ruci"] = novi
        spremi_u_bazu(baza)
        st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data["u_ruci"]:
    st.subheader("📥 Nove sličice:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            st.image(get_file_path(br))
            if st.button(f"Zalijepi #{br}", key=f"stick_{br}_{i}"):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. TRŽNICA (FIX ZA 413 I PONUDE) ---
st.header("🔄 Tržnica Sličica")
t1, t2 = st.tabs(["Dostupne razmjene", "Moje ponude"])

with t1:
    ostali = [k for k in baza.keys() if k != ja]
    for k in ostali:
        fale_meni = set(range(1, 459)) - set(moj_data["album"])
        njegovi_dupli = set(baza[k].get("duplikati", []))
        interes = njegovi_dupli.intersection(fale_meni)
        
        if interes:
            st.info(f"💡 **{k}** nudi: `{list(interes)}`")
            dajem = st.multiselect(f"Daješ za ove sličice?", moj_data["duplikati"], key=f"sel_off_{k}")
            trazim = st.multiselect(f"Uzimaš od {k}?", list(interes), key=f"sel_want_{k}")
            
            if st.button(f"Pošalji ponudu igraču {k}", key=f"btn_send_{k}"):
                if dajem and trazim:
                    baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")
                    st.rerun()

with t2:
    if not moj_data["ponude"]:
        st.write("Nema novih ponuda.")
    else:
        for idx, p in enumerate(list(moj_data["ponude"])):
            st.warning(f"📩 **{p['od']}** nudi {p['nudi']} za tvoje {p['trazi']}")
            ca, cb = st.columns(2)
            if ca.button("✅ Prihvati", key=f"acc_{idx}"):
                od_koga = p['od']
                # Transfer sličica i BRISANJE iz duplikata
                for s in p["nudi"]:
                    if s not in moj_data["album"]: moj_data["album"].append(s)
                    if s in baza[od_koga]["duplikati"]: baza[od_koga]["duplikati"].remove(s)
                for s in p["trazi"]:
                    if s not in baza[od_koga]["album"]: baza[od_koga]["album"].append(s)
                    if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
                
                moj_data["ponude"].pop(idx)
                spremi_u_bazu(baza)
                st.rerun()
            if cb.button("❌ Odbij", key=f"rej_{idx}"):
                moj_data["ponude"].pop(idx)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 7. ALBUM GRID ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 15px; justify-items:center;">'
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:130px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">'
    else:
        content = f'<div style="width:130px; height:180px; background:rgba(0,0,0,0.5); border:1px solid #555; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#aaa; font-family:sans-serif;">Fali #{i}</div>'
    grid_html += f'<div>{content}<div style="color:white; text-align:center; margin-top:5px; font-size:12px;">Br. {i}</div></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
components.html(grid_html, height=1000)
