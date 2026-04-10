import streamlit as st
import random
import os
import base64
import json
from datetime import datetime

# --- 1. OSNOVNE POSTAVKE ---
st.set_page_config(page_title="Zagor Album", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ČISTI CSS ZA POZADINU
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    .stMarkdown, p, h1, h2, h3, span {{ color: white !important; }}
</style>
''', unsafe_allow_html=True)

def get_file_path(broj):
    # Fix za putanje slika
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 2. BAZA ---
DB_FILE = "album_baza.json"
def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}
def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. KORISNIK I ČIŠĆENJE 413 ---
st.title("🛡️ Zagor Digitalni Album")
ja = st.text_input("👤 Unesi ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
# Automatsko čišćenje duplikata koji su zalijepljeni
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. SIGURNI BROJČANIK (BEZ REZANJA) ---
st.write("---")
col_b1, col_b2 = st.columns(2)
with col_b1:
    st.subheader(f"📖 Zalijepljeno: {len(moj_data['album'])}/458")
with col_b2:
    st.subheader(f"📦 Paketići: {moj_data['paketi']}")

if st.button("🎁 OTVORI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        moj_data["u_ruci"] = random.sample(range(1, 459), 5)
        spremi_u_bazu(baza)
        st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data.get("u_ruci"):
    st.write("### 📥 Sličice u ruci:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"stick_{br}_{i}", use_container_width=True):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. ALBUM (ČISTI STREAMLIT COLUMNS) ---
st.subheader("📖 Pregled Albuma")
opcije = [f"{i}-{min(i+14, 458)}" for i in range(1, 459, 15)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

# Prikaz 15 slika pomoću nativnih stupaca (5 po redu)
for row in range(3):
    cols = st.columns(5)
    for col in range(5):
        slicica_id = start + (row * 5) + col
        if slicica_id <= end:
            with cols[col]:
                if slicica_id in moj_data["album"]:
                    st.image(get_file_path(slicica_id), caption=f"Br. {slicica_id}", use_container_width=True)
                else:
                    # Prazan okvir bez HTML-a koji može "puknuti"
                    st.markdown(f"🔳 **Fali #{slicica_id}**")
                    st.write(f"ID: {slicica_id}")
