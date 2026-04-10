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

# --- 3. IDENTIFIKACIJA KORISNIKA ---
# Ime držimo skroz gore, ali diskretno
ja = st.text_input("👤 Tvoje kolekcionarsko ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": []}
    spremi_u_bazu(baza)

# Popravak za stare korisnike (KeyError fix)
if "ponude" not in baza[ja]: baza[ja]["ponude"] = []
if "paketi" not in baza[ja]: baza[ja]["paketi"] = 10
if "vrijeme" not in baza[ja]: baza[ja]["vrijeme"] = str(datetime.now())

moj_data = baza[ja]

# --- 4. LOGIKA VREMENA ZA PAKETIĆE ---
zadnje = datetime.fromisoformat(moj_data["vrijeme"])
preostalo = (zadnje + timedelta(minutes=30)) - datetime.now()

if preostalo.total_seconds() <= 0:
    moj_data["paketi"] += 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)
    st.rerun()

# --- 5. POZADINA I DIZAJN ---
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ background-color: rgba(0,0,0,0.7); }}
    .main-stat {{ font-size: 24px; font-weight: bold; color: white; }}
    </style>
''', unsafe_allow_html=True)

# --- 6. VRH: STATISTIKA I PAKETIĆI ---
st.title("🛡️ Zagor Digitalni Album")

# Red s gumbom i metrikama koji je nedostajao
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
col1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
col2.metric("Paketići", moj_data["paketi"])
mins, secs = divmod(int(preostalo.total_seconds()), 60)
col3.write(f"⏳ Novi za:\n**{mins:02d}:{secs:02d}**")

if col4.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0:
        moj_data["paketi"] -= 1
        nove = [random.randint(1, 458) for _ in range(5)]
        # Automatsko lijepljenje ili slanje u duplikate
        for n in nove:
            if n in moj_data["album"]:
                moj_data["duplikati"].append(n)
            else:
                moj_data["album"].append(n)
        spremi_u_bazu(baza)
        st.rerun()

st.divider()

# --- 7. TRŽNICA (Sada u Expanderu da ne smeta albumu) ---
with st.expander("🔄 OTVORI TRŽNICU I RAZMJENU"):
    tab1, tab2 = st.tabs(["Dostupne razmjene", "Moje ponude"])
    
    with tab1:
        drugi_k = [k for k in baza.keys() if k != ja]
        for drugi in drugi_k:
            njegovi_dupli = set(baza[drugi].get("duplikati", []))
            meni_fale = set(range(1, 459)) - set(moj_data["album"])
            interes = njegovi_dupli.intersection(meni_fale)
            if interes:
                st.write(f"Kolekcionar **{drugi}** ima što ti treba: {list(interes)}")
                dajem = st.multiselect(f"Ponudi svoje duplikate za {drugi}:", moj_data.get("duplikati", []), key=f"d_{drugi}")
                trazim = st.multiselect(f"Traži od njega:", list(interes), key=f"t_{drugi}")
                if st.button(f"Pošalji ponudu prema {drugi}"):
                    baza[drugi]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim, "status": "na_cekanju"})
                    spremi_u_bazu(baza)
                    st.success("Poslano!")

    with tab2:
        for idx, p in enumerate(moj_data["ponude"]):
            if p.get("status") == "na_cekanju":
                st.info(f"**{p['od']}** nudi {p['nudi']} za tvoje {p['trazi']}")
                ca, cb = st.columns(2)
                if ca.button("✅ Prihvati", key=f"acc_{idx}"):
                    for s in p["nudi"]: 
                        if s not in moj_data["album"]: moj_data["album"].append(s)
                    p["status"] = "prihvaceno"
                    spremi_u_bazu(baza)
                    st.rerun()
                if cb.button("❌ Odbij", key=f"rej_{idx}"):
                    p["status"] = "odbijeno"
                    spremi_u_bazu(baza)
                    st.rerun()

# --- 8. PREGLED ALBUMA (Dizajn iz image_601984.jpg) ---
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

full_html = f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 35px; justify-items:center; padding: 10px;">{grid_items}</div>'

import streamlit.components.v1 as components
components.html(full_html, height=1100, scrolling=False)

time.sleep(1)
st.rerun()
