import streamlit as st
import random
import os
import base64
import time
import json
from datetime import datetime, timedelta

# --- 1. KONFIGURACIJA I STIL ---
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

# --- 2. BAZA PODATAKA ---
DB_FILE = "album_baza.json"

def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def spremi_u_bazu(baza_podataka):
    with open(DB_FILE, "w") as f: json.dump(baza_podataka, f)

baza = ucitaj_bazu()

# --- 3. PROFIL I SIGURNOSNE PROVJERE ---
st.title("🛡️ Zagor: Digitalni Album")
ja = st.text_input("👤 Tvoje ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# Popravak svih mogućih grešaka u strukturi podataka (TypeError/KeyError)
obavezni_kljucevi = {
    "album": [], "duplikati": [], "paketi": 10, 
    "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []
}
for kljuc, default in obavezni_kljucevi.items():
    if kljuc not in moj_data or (isinstance(default, list) and not isinstance(moj_data[kljuc], list)):
        moj_data[kljuc] = default

spremi_u_bazu(baza)

# --- 4. TAJMER ZA NOVE PAKETE ---
zadnje = datetime.fromisoformat(str(moj_data.get("vrijeme", datetime.now())))
preostalo = (zadnje + timedelta(minutes=30)) - datetime.now()

if preostalo.total_seconds() <= 0:
    moj_data["paketi"] = moj_data.get("paketi", 0) + 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)
    st.rerun()

# --- 5. VIZUALNI IDENTITET ---
bg_data = get_base64('image_50927d.jpg')
if bg_data:
    st.markdown(f'''<style>.stApp {{ background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}"); background-size: cover; background-attachment: fixed; }} [data-testid="stSidebar"] {{ display: none; }} </style>''', unsafe_allow_html=True)

# --- 6. ZAGLAVLJE I OTVARANJE PAKETIĆA ---
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
c1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
c2.metric("Paketići", moj_data["paketi"])
mins, secs = divmod(int(preostalo.total_seconds()), 60)
c3.write(f"⏳ Novi za:\n**{mins:02d}:{secs:02d}**")

if c4.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0:
        moj_data["paketi"] -= 1
        
        # --- FIX: STROGA ZABRANA DUPLIKATA UNUTAR PAKETA ---
        novi_sadrzaj = []
        while len(novi_sadrzaj) < 5:
            broj = random.randint(1, 458)
            if broj not in novi_sadrzaj: # Provjera unikatnosti unutar samog izvlačenja
                novi_sadrzaj.append(broj)
        
        moj_data["u_ruci"].extend(novi_sadrzaj)
        spremi_u_bazu(baza)
        st.rerun()

# --- 7. RUČNO LIJEPLJENJE (PROZOR "U RUCI") ---
if moj_data["u_ruci"]:
    st.subheader("📥 Nove sličice (klikni na gumb za lijepljenje):")
    ruka_cols = st.columns(5)
    # Prikazujemo prvih 5 iz ruku
    za_prikaz = list(moj_data["u_ruci"])[:5]
    for idx, br in enumerate(za_prikaz):
        with ruka_cols[idx]:
            st.image(get_file_path(br), width=150)
            if st.button(f"Zalijepi #{br}", key=f"stick_{idx}_{br}"):
                if br in moj_data["album"]:
                    if br not in moj_data["duplikati"]:
                        moj_data["duplikati"].append(br)
                    st.toast(f"Duplikat #{br} spremljen u razmjenu.")
                else:
                    moj_data["album"].append(br)
                    st.toast(f"Sličica #{br} uspješno zalijepljena!")
                
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 8. TRŽNICA (RAZMJENA) ---
with st.expander("🔄 TRŽNICA I PONUDE"):
    t1, t2 = st.tabs(["Dostupne razmjene", "Pridružene ponude"])
    with t1:
        ostali = [k for k in baza.keys() if k != ja]
        for kolekcionar in ostali:
            njegovi_dupli = set(baza[kolekcionar].get("duplikati", []))
            meni_fale = set(range(1, 459)) - set(moj_data["album"])
            interes = njegovi_dupli.intersection(meni_fale)
            if interes:
                st.write(f"**{kolekcionar}** ima što ti treba: {list(interes)}")
                nudi = st.multiselect(f"Tvoji dupli za {kolekcionar}:", moj_data["duplikati"], key=f"n_{kolekcionar}")
                trazi = st.multiselect(f"Uzmi od njega:", list(interes), key=f"t_{kolekcionar}")
                if st.button(f"Pošalji ponudu kolekcionaru {kolekcionar}"):
                    if "ponude" not in baza[kolekcionar]: baza[kolekcionar]["ponude"] = []
                    baza[kolekcionar]["ponude"].append({"od": ja, "nudi": nudi, "trazi": trazi, "status": "na_cekanju"})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")
    with t2:
        for p_idx, p in enumerate(moj_data.get("ponude", [])):
            if p.get("status") == "na_cekanju":
                st.info(f"**{p['od']}** ti nudi {p['nudi']} za tvoje {p['trazi']}")
                ca, cb = st.columns(2)
                if ca.button("✅ Prihvati", key=f"acc_{p_idx}"):
                    for s in p["nudi"]: 
                        if s not in moj_data["album"]: moj_data["album"].append(s)
                    p["status"] = "prihvaceno"
                    spremi_u_bazu(baza)
                    st.rerun()
                if cb.button("❌ Odbij", key=f"rej_{p_idx}"):
                    p["status"] = "odbijeno"
                    spremi_u_bazu(baza)
                    st.rerun()

# --- 9. ALBUM GRID (5 STUPACA) ---
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
