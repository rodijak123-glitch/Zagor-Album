import streamlit as st
import random
import os
import base64
import time
import json
from datetime import datetime, timedelta

# --- 1. POSTAVKE I STIL ---
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

# Sigurnosne provjere strukture (TypeError/KeyError fix)
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data or not isinstance(moj_data[k], list):
        moj_data[k] = []
if "paketi" not in moj_data: moj_data["paketi"] = 10

spremi_u_bazu(baza)

# --- 4. TAJMER ---
zadnje = datetime.fromisoformat(str(moj_data.get("vrijeme", datetime.now())))
preostalo = (zadnje + timedelta(minutes=30)) - datetime.now()

if preostalo.total_seconds() <= 0:
    moj_data["paketi"] += 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)
    st.rerun()

# --- 5. POZADINA ---
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'''<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }}</style>''', unsafe_allow_html=True)

# --- 6. ZAGLAVLJE ---
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])
mins, secs = divmod(int(preostalo.total_seconds()), 60)
c3.write(f"⏳ Novi za:\n**{mins:02d}:{secs:02d}**")

# --- 7. LOGIKA OTVARANJA (JEDNA PO JEDNA) ---
if c4.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        
        # Generiramo 5 unikatnih sličica za ovaj paket
        novi_paket = []
        while len(novi_paket) < 5:
            broj = random.randint(1, 458)
            if broj not in novi_paket:
                novi_paket.append(broj)
        
        # Spremanje u "ruku" za postepeno prikazivanje
        moj_data["u_ruci"] = novi_paket
        spremi_u_bazu(baza)
        
        # Animacijski efekt - Streamlit će se osvježiti i prikazati prvu
        st.rerun()

# --- 8. PRIKAZ SLIČICA IZ PAKETIĆA ---
if moj_data["u_ruci"]:
    st.subheader("📥 Otvaranje paketića...")
    
    # Prikazujemo samo onoliko mjesta koliko ima sličica u ruku
    ruka_cols = st.columns(5)
    
    # Uzimamo trenutne sličice
    trenutne = moj_data["u_ruci"]
    
    for i in range(5):
        with ruka_cols[i]:
            if i < len(trenutne):
                # Sličica je u "ruci" i čeka na lijepljenje
                br = trenutne[i]
                st.image(get_file_path(br), use_container_width=True)
                if st.button(f"Zalijepi #{br}", key=f"s_{i}_{br}"):
                    if br in moj_data["album"]:
                        if br not in moj_data["duplikati"]:
                            moj_data["duplikati"].append(br)
                        st.toast(f"Duplikat #{br} ide u razmjenu!")
                    else:
                        moj_data["album"].append(br)
                        st.toast(f"#{br} zalijepljena u album!")
                    
                    # Uklanjamo samo tu jednu kliknutu sličicu
                    moj_data["u_ruci"].pop(i)
                    spremi_u_bazu(baza)
                    st.rerun()
            else:
                # Prazan okvir nakon što je sličica zalijepljena
                st.markdown('<div style="height:200px; border:2px dashed #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#555;">Prazno</div>', unsafe_allow_html=True)

st.divider()

# --- 9. TRŽNICA (RAZMJENA) ---
with st.expander("🔄 TRŽNICA I PONUDE"):
    t1, t2 = st.tabs(["Dostupne razmjene", "Moje ponude"])
    with t1:
        for k in [kor for kor in baza.keys() if kor != ja]:
            dupli = set(baza[k].get("duplikati", []))
            fale = set(range(1, 459)) - set(moj_data["album"])
            interes = dupli.intersection(fale)
            if interes:
                st.write(f"**{k}** nudi: {list(interes)}")
                dajem = st.multiselect(f"Tvoji dupli za {k}:", moj_data["duplikati"], key=f"n_{k}")
                trazi = st.multiselect(f"Tražiš od njega:", list(interes), key=f"t_{k}")
                if st.button(f"Pošalji ponudu - {k}"):
                    if "ponude" not in baza[k]: baza[k]["ponude"] = []
                    baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazi, "status": "na_cekanju"})
                    spremi_u_bazu(baza)
                    st.success("Poslano!")
    with t2:
        for p_idx, p in enumerate(moj_data.get("ponude", [])):
            if p.get("status") == "na_cekanju":
                st.info(f"**{p['od']}** nudi {p['nudi']} za tvoje {p['trazi']}")
                if st.button("✅ Prihvati", key=f"acc_{p_idx}"):
                    for s in p["nudi"]: 
                        if s not in moj_data["album"]: moj_data["album"].append(s)
                    p["status"] = "prihvaceno"
                    spremi_u_bazu(baza)
                    st.rerun()

# --- 10. ALBUM GRID (5 STUPACA) ---
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
    grid_items += f'<div style="text-align:center; padding-bottom: 25px;">{content}<div style="color:white; font-weight:bold; margin-top:10px; font-family:sans-serif;">Br. {i}</div></div>'

import streamlit.components.v1 as components
components.html(f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 30px; justify-items:center; padding: 10px;">{grid_items}</div>', height=1150)

time.sleep(1)
st.rerun()
