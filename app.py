import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import os
import base64
import json
from datetime import datetime, timedelta

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album: Vječna Baza", layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1MvFhwD--5BbQ-tdWB2JrO0yXmHV37RxBqlzLVYpYja4/edit#gid=0"

# --- FUNKCIJA ZA POVEZIVANJE S GOOGLE SHEETS ---
# Napomena: Za pravi rad na serveru, morat ćeš dodati google_auth u Secrets
def ucitaj_iz_sheeta():
    try:
        # Čitamo tablicu kao CSV (javni link)
        csv_url = SHEET_URL.replace('/edit#gid=', '/export?format=csv&gid=')
        df = pd.read_csv(csv_url)
        # Pretvaramo u rječnik koji naš kod razumije
        baza = {}
        for _, row in df.iterrows():
            baza[row['korisnik']] = json.loads(row['podaci'])
        return baza
    except:
        return {}

def spremi_u_sheet(baza_data):
    # Za pisanje u Google Sheets na Streamlit Cloudu, 
    # najsigurnije je koristiti st.connection ili gspread sa Secrets.
    # Privremeno ćemo koristiti lokalni JSON ako pisanje u Sheet ne uspije odmah
    with open("album_baza.json", "w") as f:
        json.dump(baza_data, f)
    # Ovdje bi išao kod za gspread update koji šalje podatke natrag u Sheet

# --- OSTATAK KODA (Zagor Logika) ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed; color: white;
    }}
    .metric-box {{
        background: rgba(255, 75, 75, 0.3);
        padding: 20px; border-radius: 15px; border: 2px solid #ff4b4b;
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

# Učitavanje baze (Sada primarno iz Sheeta)
baza = ucitaj_iz_sheeta()

st.title("🏹 Zagor: Digitalni Album (Vječni)")
ja = st.text_input("Unesi svoje ime:").strip()

if not ja:
    st.warning("Prijavi se za početak sakupljanja!")
    st.stop()

if ja not in baza:
    baza[ja] = {
        "album": [], "duplikati": [], "paketi": 10, 
        "ponude": [], "u_ruci": [], 
        "zadnji_gratis": str(datetime.now() - timedelta(minutes=30))
    }
    spremi_u_sheet(baza)

moj_data = baza[ja]

# --- (Ovdje ide sav onaj kod za paketiće, timer i album koji smo već sredili) ---
# ... (Timer, Lijepljenje, Tržnica, Album Grid) ...

# SAMO NA KRAJU DODAJ OVO ZA ALBUM GRID DA BUDE 1200px
st.divider()
st.subheader("📖 Tvoj Album")
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
    grid_html += f'<div>{content}<div style="color:white; text-align:center; margin-top:5px; font-weight:bold;">Br. {i}</div></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
components.html(grid_html, height=1200)
