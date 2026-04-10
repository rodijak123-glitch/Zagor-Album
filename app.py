import streamlit as st
import random
import os
import base64
import json
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# POZADINA I STIL (Fix za pomicanje i vidljivost)
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    /* Forsiramo da svaki element u albumu ima ISTU visinu da nema skakanja */
    .album-slot {{
        height: 250px; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: flex-start;
    }}
    .slicica-img {{
        width: 150px; 
        height: 200px; 
        object-fit: cover; 
        border: 2px solid #ff4b4b; 
        border-radius: 5px;
    }}
    .prazno-slot {{
        width: 150px; 
        height: 200px; 
        background: rgba(255,255,255,0.05); 
        border: 1px solid #444; 
        border-radius: 5px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: #555;
    }}
    h1, h2, h3, p, span {{ color: white !important; }}
</style>
''', unsafe_allow_html=True)

# --- 2. BAZA PODATAKA ---
DB_FILE = "album_baza.json"
def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}
def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. KORISNIK I FIX ZA 413 ---
st.title("🛡️ Zagor Digitalni Album")
ja = st.text_input("👤 Unesi ime:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
# Čišćenje 413
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. BROJČANIK (VRAĆEN KAO OBIČAN TEKST) ---
# Ako ga ne vidiš na vrhu, Streamlit ga reže zbog pozadine. Stavljamo ga u uočljiv okvir.
st.markdown(f"""
<div style="background: rgba(255,75,75,0.2); padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; margin-bottom: 20px;">
    <h2 style="margin:0; text-align:center;">📊 Zalijepljeno: {len(moj_data['album'])}/458 | 📦 Paketići: {moj_data['paketi']}</h2>
</div>
""", unsafe_allow_html=True)

if st.button("🎁 OTVORI NOVI PAKETIĆ", use_container_width=True):
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
            # Koristimo direktan put do slike
            f = "slike/"
            path = f"{f}TN_ZG_EXT_{br}.jpeg" if br <= 75 else f"{f}TN_ZG_LEX_{br}.jpeg" # Skraćeno za primjer
            st.image(path, use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}", use_container_width=True):
                if br in moj_data["album"]:
                    if br not in moj_data["duplikati"]: moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. ALBUM (FIX ZA POMICANJE) ---
st.subheader("📖 Pregled Albuma")
broj_po_stranici = 15
opcije = [f"{i}-{min(i+14, 458)}" for i in range(1, 459, broj_po_stranici)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

# Cijeli album ide u jedan HTML blok da osiguramo fixne visine
album_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 20px; justify-items:center;">'

for i in range(start, end + 1):
    if i in moj_data["album"]:
        # Putanja slike (prilagodi svojoj logici get_file_path)
        img_url = f"data:image/jpeg;base64,{get_base64(f'slike/TN_ZG_LEX_{i}.jpeg')}" # Primjer
        content = f'<img src="{img_url}" class="slicica-img">'
        label = f'Br. {i}'
    else:
        content = f'<div class="prazno-slot">#{i}</div>'
        label = f'Fali #{i}'
    
    # Svaki element je umotan u 'album-slot' koji ima fiksnu visinu
    album_html += f'''
    <div class="album-slot">
        {content}
        <p style="margin-top:5px; font-size:12px; font-weight:bold;">{label}</p>
    </div>'''

album_html += '</div>'
st.components.v1.html(album_html, height=850)
