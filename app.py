import streamlit as st
import random
import os
import base64
import time
import json
from datetime import datetime, timedelta

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionari", layout="wide")

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

# --- 2. LOGIKA BAZE PODATAKA ---
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

# --- 3. PROFIL KORISNIKA I FIX ZA TYPEERROR ---
st.title("🛡️ Zagor: Digitalni Album")
ja = st.text_input("👤 Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

# Sigurnosna provjera svih ključeva (popravlja image_608a60.png)
moj_data = baza[ja]
default_keys = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
for kljuc, default in default_keys.items():
    if kljuc not in moj_data or (kljuc in ["album", "duplikati", "ponude", "u_ruci"] and not isinstance(moj_data[kljuc], list)):
        moj_data[kljuc] = default

spremi_u_bazu(baza)

# --- 4. TAJMER ZA NOVE PAKETE ---
zadnje = datetime.fromisoformat(str(moj_data["vrijeme"]))
preostalo = (zadnje + timedelta(minutes=30)) - datetime.now()

if preostalo.total_seconds() <= 0:
    moj_data["paketi"] += 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)
    st.rerun()

# --- 5. STIL I POZADINA ---
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}");
            background-size: cover; background-attachment: fixed;
        }}
        [data-testid="stSidebar"] {{ display: none; }}
        </style>
    ''', unsafe_allow_html=True)

# --- 6. STATISTIKA I OTVARANJE ---
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])
mins, secs = divmod(int(preostalo.total_seconds()), 60)
c3.write(f"⏳ Novi za:\n**{mins:02d}:{secs:02d}**")

if c4.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0:
        moj_data["paketi"] -= 1
        moj_data["u_ruci"].extend([random.randint(1, 458) for _ in range(5)])
        spremi_u_bazu(baza)
        st.rerun()

# --- 7. RUČNO LIJEPLJENJE (PROZOR "U RUCI") ---
if moj_data["u_ruci"]:
    st.subheader("📥 Nove sličice (klikni na sliku za lijepljenje):")
    ruka_cols = st.columns(5)
    # Uzimamo kopiju da izbjegnemo greške pri brisanju tokom petlje
    trenutne_u_ruci = list(moj_data["u_ruci"])[:5]
    for idx, br in enumerate(trenutne_u_ruci):
        with ruka_cols[idx]:
            st.image(get_file_path(br), width=140)
            if st.button(f"Zalijepi #{br}", key=f"btn_st_{idx}_{br}"):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                    st.toast(f"Duplikat #{br} ide u razmjenu!")
                else:
                    moj_data["album"].append(br)
                    st.toast(f"Sličica #{br} zalijepljena!")
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 8. TRŽNICA (RAZMJENA) ---
with st.expander("🔄 TRŽNICA I PONUDE DRUGIH"):
    t1, t2 = st.tabs(["Dostupne razmjene", "Pridružene ponude"])
    with t1:
        ostali = [k for k in baza.keys() if k != ja]
        for kolekcionar in ostali:
            njegovi_dupli = set(baza[kolekcionar].get("duplikati", []))
            meni_fale = set(range(1, 459)) - set(moj_data["album"])
            interes = njegovi_dupli.intersection(meni_fale)
            if interes:
                st.write(f"**{kolekcionar}** nudi: {list(interes)}")
                nudi_moje = st.multiselect(f"Što daješ iz svojih duplikata?", moj_data["duplikati"], key=f"off_{kolekcionar}")
                trazi_njegove = st.multiselect(f"Što želiš od njega?", list(interes), key=f"get_{kolekcionar}")
                if st.button(f"Pošalji ponudu za {kolekcionar}"):
                    if "ponude" not in baza[kolekcionar]: baza[kolekcionar]["ponude"] = []
                    baza[kolekcionar]["ponude"].append({"od": ja, "nudi": nudi_moje, "trazi": trazi_njegove, "status": "na_cekanju"})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")
    with t2:
        for p_idx, ponuda in enumerate(moj_data.get("ponude", [])):
            if ponuda.get("status") == "na_cekanju":
                st.info(f"Kolekcionar **{ponuda['od']}** nudi {ponuda['nudi']} za tvoje {ponuda['trazi']}")
                ca, cb = st.columns(2)
                if ca.button("✅ Prihvati", key=f"acc_{p_idx}"):
                    # Zamjena (osnovna logika)
                    for s in ponuda["nudi"]: 
                        if s not in moj_data["album"]: moj_data["album"].append(s)
                    ponuda["status"] = "prihvaceno"
                    spremi_u_bazu(baza)
                    st.rerun()
                if cb.button("❌ Odbij", key=f"rej_{p_idx}"):
                    ponuda["status"] = "odbijeno"
                    spremi_u_bazu(baza)
                    st.rerun()

# --- 9. PRIKAZ ALBUMA (HTML GRID) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_items = ""
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; height:200px; object-fit:cover; border-radius:10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.5);">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.8); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888; font-family:sans-serif; font-size:14px;">Fali #{i}</div>'
    
    grid_items += f'<div style="text-align:center; padding-bottom: 25px;">{content}<div style="color:white; font-weight:bold; margin-top:10px; font-family:sans-serif; font-size:14px;">Br. {i}</div></div>'

import streamlit.components.v1 as components
full_html = f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 30px; justify-items:center; padding: 10px;">{grid_items}</div>'
components.html(full_html, height=1150, scrolling=False)

# Osvježavanje svake sekunde zbog brojača
time.sleep(1)
st.rerun()
