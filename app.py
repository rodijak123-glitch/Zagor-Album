import streamlit as st
import random
import os
import base64
import json
from datetime import datetime, timedelta

# --- 1. POSTAVKE I POMOĆNE FUNKCIJE ---
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

# --- 2. BAZA PODATAKA (JSON) ---
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

# --- 3. PROFIL KORISNIKA I SIGURNOST ---
st.title("🛡️ Zagor: Digitalni Album")
ja = st.text_input("👤 Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# Popravak strukture podataka da izbjegnemo KeyError
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data or not isinstance(moj_data[k], list):
        moj_data[k] = []
if "paketi" not in moj_data: moj_data["paketi"] = 10

# --- 4. TAJMER ZA PAKETIĆE (Bez rerun petlje) ---
zadnje = datetime.fromisoformat(str(moj_data.get("vrijeme", datetime.now())))
if (datetime.now() - zadnje).total_seconds() > 1800:
    moj_data["paketi"] += 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)

# --- 5. POZADINA ---
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'''<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }}</style>''', unsafe_allow_html=True)

# --- 6. STATISTIKA I OTVARANJE PAKETIĆA ---
c1, c2, c3 = st.columns([1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])

if c3.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        # Strogo unikatnih 5 sličica unutar paketa
        novi = []
        while len(novi) < 5:
            broj = random.randint(1, 458)
            if broj not in novi: novi.append(broj)
        moj_data["u_ruci"] = novi
        spremi_u_bazu(baza)
        st.rerun()

# --- 7. PRIKAZ "U RUCI" (JEDNA PO JEDNA) ---
if moj_data["u_ruci"]:
    st.subheader("📥 Nove sličice iz paketa:")
    ruka_cols = st.columns(5)
    trenutne = list(moj_data["u_ruci"])
    for i in range(5):
        with ruka_cols[i]:
            if i < len(trenutne):
                br = trenutne[i]
                st.image(get_file_path(br), use_container_width=True)
                if st.button(f"Zalijepi #{br}", key=f"p_{i}_{br}"):
                    if br in moj_data["album"]:
                        moj_data["duplikati"].append(br)
                        st.toast(f"#{br} je duplikat!")
                    else:
                        moj_data["album"].append(br)
                        st.toast(f"#{br} zalijepljena!")
                    moj_data["u_ruci"].remove(br)
                    spremi_u_bazu(baza)
                    st.rerun()
            else:
                st.markdown('<div style="height:100px; border:1px dashed #555; border-radius:10px;"></div>', unsafe_allow_html=True)

st.divider()

# --- 8. TRŽNICA (KOMPLETNA SA SVIM GUMBIMA) ---
st.header("🔄 Tržnica Sličica")
t1, t2 = st.tabs(["Dostupne razmjene", "Moje ponude"])

with t1:
    ostali = [k for k in baza.keys() if k != ja]
    found_trade = False
    for k in ostali:
        njegovi_dupli = set(baza[k].get("duplikati", []))
        meni_fale = set(range(1, 459)) - set(moj_data["album"])
        interes = njegovi_dupli.intersection(meni_fale)
        
        if interes:
            found_trade = True
            st.write(f"🤝 **{k}** nudi sličice koje ti trebaju: `{list(interes)}`")
            dajem = st.multiselect(f"Što nudiš iz svojih duplikata?", moj_data["duplikati"], key=f"off_{k}")
            trazim = st.multiselect(f"Što želiš od njega?", list(interes), key=f"want_{k}")
            
            if st.button(f"Pošalji ponudu igraču {k}", key=f"btn_{k}"):
                if dajem and trazim:
                    if "ponude" not in baza[k]: baza[k]["ponude"] = []
                    baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim, "status": "na_cekanju"})
                    spremi_u_bazu(baza)
                    st.success(f"Ponuda poslana igraču {k}!")
                else:
                    st.warning("Odaberi sličice za razmjenu!")
    if not found_trade:
        st.info("Trenutno nitko ne nudi sličice koje ti nedostaju.")

with t2:
    for idx, p in enumerate(moj_data.get("ponude", [])):
        if p.get("status") == "na_cekanju":
            st.warning(f"📩 **{p['od']}** ti nudi #{p['nudi']} za tvoje #{p['trazi']}")
            ca, cb = st.columns(2)
            if ca.button("✅ Prihvati", key=f"acc_{idx}"):
                # Dodaj u album
                for s in p["nudi"]:
                    if s not in moj_data["album"]: moj_data["album"].append(s)
                # Makni iz duplikata (traženo)
                for s in p["trazi"]:
                    if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
                p["status"] = "prihvaceno"
                spremi_u_bazu(baza)
                st.rerun()
            if cb.button("❌ Odbij", key=f"rej_{idx}"):
                p["status"] = "odbijeno"
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 9. ALBUM GRID (5 STUPACA) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = ""
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:140px; border-radius:10px; box-shadow: 2px 2px 5px black;">'
    else:
        content = f'<div style="width:140px; height:190px; background:#333; border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#777; font-family:sans-serif;">Fali #{i}</div>'
    grid_html += f'<div style="text-align:center;">{content}<div style="color:white; font-size:12px; margin-top:5px;">Br. {i}</div></div>'

import streamlit.components.v1 as components
# Bez st.rerun() na kraju koda kako bi se izbjeglo treperenje
components.html(f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 20px; justify-items:center;">{grid_html}</div>', height=1000)
