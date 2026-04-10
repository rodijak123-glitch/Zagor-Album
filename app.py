import streamlit as st
import random
import os
import base64
import time
import json
from datetime import datetime, timedelta

# --- 1. POSTAVKE ---
st.set_page_config(page_title="Zagor: Kolekcionari", layout="wide")

# Funkcija za slike ostaje ista jer radi savršeno
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

# --- 2. JEDNOSTAVNA LOKALNA BAZA (JSON) ---
# Pošto si tražio najjednostavnije, koristit ćemo .json datoteku koja se sama stvara
DB_FILE = "album_baza.json"

def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def spremi_u_bazu(baza):
    with open(DB_FILE, "w") as f: json.dump(baza, f)

baza_podataka = ucitaj_bazu()

# --- 3. IDENTIFIKACIJA KORISNIKA ---
st.title("🛡️ Zagor: Kolekcionari")
korisnik = st.text_input("Unesi svoje ime (Kolekcionar):", value="Gost").strip()

if korisnik not in baza_podataka:
    baza_podataka[korisnik] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now())}
    spremi_u_bazu(baza_podataka)

# Prebacujemo podatke u session_state za rad
korisnik_data = baza_podataka[korisnik]

# --- 4. LOGIKA VREMENA ---
zadnje = datetime.fromisoformat(korisnik_data["vrijeme"])
preostalo = (zadnje + timedelta(minutes=30)) - datetime.now()

if preostalo.total_seconds() <= 0:
    korisnik_data["paketi"] += 2
    korisnik_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza_podataka)
    st.rerun()

# --- 5. POZADINA I DIZAJN (Tvoj pobjednički stil) ---
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    [data-testid="stSidebar"] {{ display: none; }}
    </style>
''', unsafe_allow_html=True)

# --- 6. GLAVNI METERI ---
c1, c2, c3 = st.columns([1, 1, 1])
c1.metric("Zalijepljeno", f"{len(korisnik_data['album'])}/458")
c2.metric("Paketići", korisnik_data["paketi"])
mins, secs = divmod(int(preostalo.total_seconds()), 60)
c3.warning(f"⏳ Novi paketići: {mins:02d}:{secs:02d}")

if st.button("📦 OTVORI PAKETIĆ", use_container_width=True):
    if korisnik_data["paketi"] > 0:
        korisnik_data["paketi"] -= 1
        nove = [random.randint(1, 458) for _ in range(5)]
        # Odmah provjeravamo duplikate
        for n in nove:
            if n in korisnik_data["album"]:
                korisnik_data["duplikati"].append(n)
                st.toast(f"Duplikat! #{n} ide u razmjenu.")
            else:
                korisnik_data["album"].append(n)
        spremi_u_bazu(baza_podataka)
        st.rerun()

# --- 7. PRIKAZ DUPLIKATA ZA RAZMJENU ---
if korisnik_data["duplikati"]:
    with st.expander("🔄 Moji Duplikati za razmjenu"):
        st.write(f"Imaš duplikate: {list(set(korisnik_data['duplikati']))}")

st.divider()

# --- 8. ALBUM GRID (Izolirani HTML iz image_601984.jpg) ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_items = ""
for i in range(start, end + 1):
    if i in korisnik_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:150px; height:200px; object-fit:cover; border-radius:10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.5);">'
    else:
        content = f'<div style="width:150px; height:200px; background:rgba(40,40,40,0.8); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888; font-family:sans-serif;">Fali #{i}</div>'
    
    grid_items += f'''
        <div style="text-align:center; padding-bottom: 20px;">
            {content}
            <div style="color:white; font-weight:bold; margin-top:10px; font-family:sans-serif; font-size:14px;">Br. {i}</div>
        </div>
    '''

full_html = f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 35px; justify-items:center; padding: 10px;">{grid_items}</div>'

import streamlit.components.v1 as components
components.html(full_html, height=1100, scrolling=False)

time.sleep(1)
st.rerun()
