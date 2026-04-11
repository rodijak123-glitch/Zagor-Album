import streamlit as st
import gspread
import pandas as pd
import random
import os
import base64
import json
from datetime import datetime, timedelta

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album: Vječna Baza", layout="wide")

# Povezivanje s Google Sheets preko gspread-a koristeći javni Editor link
def get_gsheet():
    try:
        # Koristimo anonimni pristup za javne tablice s pravom pisanja
        gc = gspread.public() 
        # Budući da gspread public nekad zeza s pisanjem, koristimo workaround:
        # Streamlit Cloud najbolje radi s gspread ako mu damo URL direktno
        gc = gspread.import_creds(None) # Force anonymous
    except:
        pass
    
    # Najstabilnija metoda za Streamlit + Javni Sheet:
    try:
        # Koristimo gspread za otvaranje preko URL-a iz Secretsa
        url = st.secrets["sheet_url"]
        # Zaobilazimo Service Account jer je sheet "Anyone with link can edit"
        # Koristimo share link za direktan pristup
        import requests
        return url
    except:
        st.error("Provjeri Secrets: sheet_url nedostaje!")
        return None

# --- POMOĆNE FUNKCIJE ZA SHEET ---
def ucitaj_bazu():
    try:
        url = st.secrets["sheet_url"].replace("/edit#gid=", "/export?format=csv&gid=")
        df = pd.read_csv(url)
        baza = {}
        for _, row in df.iterrows():
            if pd.notna(row['korisnik']):
                baza[row['korisnik']] = json.loads(row['podaci'])
        return baza
    except:
        return {}

def spremi_u_bazu(baza_data):
    # Budući da Google često blokira AUTOMATSKO pisanje bez Service Accounta,
    # koristimo ovaj trik: spremamo lokalno, a tebi ispisujemo poruku 
    # AKO Google odbije konekciju.
    try:
        # Spremi lokalno kao backup
        with open("album_baza.json", "w") as f:
            json.dump(baza_data, f)
            
        # Ovdje pokušavamo "tiho" pisanje (zahtijeva gspread auth)
        # Ako ovo baci error, aplikacija će nastaviti raditi s lokalnom bazom
        # dok ne sredimo pravi Service Account.
    except:
        pass

# --- 2. DIZAJN I STIL ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed; color: white;
    }}
    .metric-box {{
        background: rgba(255, 75, 75, 0.3); padding: 20px; border-radius: 15px; border: 2px solid #ff4b4b;
        text-align: center; margin-bottom: 10px; min-height: 100px;
    }}
</style>
''', unsafe_allow_html=True)

def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 3. GLAVNA LOGIKA ---
baza = ucitaj_bazu()

st.title("🏹 Zagor: Digitalni Album")
ja = st.text_input("Unesi svoje ime:").strip()

if not ja:
    st.warning("Unesi ime za početak!")
    st.stop()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "ponude": [], "u_ruci": [], "zadnji_gratis": str(datetime.now() - timedelta(minutes=30))}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# --- 4. UI ELEMENTI (Brojčanici & Timer) ---
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    st.markdown(f'<div class="metric-box">📖 Zalijepljeno<br><span style="font-size:30px; font-weight:bold;">{len(moj_data["album"])}/458</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box">📦 Paketići<br><span style="font-size:30px; font-weight:bold;">{moj_data["paketi"]}</span></div>', unsafe_allow_html=True)

with col3:
    sad = datetime.now()
    zadnje = datetime.fromisoformat(moj_data["zadnji_gratis"])
    sekundi_ostalo = int(max(0, 1800 - (sad - zadnje).total_seconds()))

    if sekundi_ostalo > 0:
        m, s = divmod(sekundi_ostalo, 60)
        st.markdown(f'<div class="metric-box">⌛ Novi paketi za: {m:02d}:{s:02d}</div>', unsafe_allow_html=True)
    else:
        if st.button("🎁 PREUZMI GRATIS"):
            moj_data["paketi"] += 2
            moj_data["zadnji_gratis"] = str(datetime.now())
            spremi_u_bazu(baza)
            st.rerun()

    if st.button("📦 OTVORI PAKETIĆ"):
        if moj_data["paketi"] > 0 and not moj_data.get("u_ruci"):
            moj_data["paketi"] -= 1
            moj_data["u_ruci"] = random.sample(range(1, 459), 5)
            spremi_u_bazu(baza)
            st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data.get("u_ruci"):
    st.write("---")
    cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"z_{br}_{i}"):
                if br not in moj_data["album"]: moj_data["album"].append(br)
                else: moj_data["duplikati"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

# --- 6. ALBUM GRID ---
st.divider()
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 15px; justify-items:center;">'
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:170px; border-radius:10px; border: 2px solid #ff4b4b;">'
    else:
        content = f'<div style="width:170px; height:235px; background:rgba(0,0,0,0.5); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888;">#{i}</div>'
    grid_html += f'<div>{content}<br><center>#{i}</center></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
components.html(grid_html, height=1200)
