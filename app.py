import streamlit as st
import random
import os
import json
from datetime import datetime

# --- 1. ČISTA POZADINA (BEZ TIGRA) ---
st.set_page_config(page_title="Zagor Album", layout="wide")

# Koristimo jednostavan CSS koji samo potamnjuje pozadinu bez vanjskih linkova
st.markdown('''
<style>
    .stApp { background-color: #0e1117; }
    .stMarkdown, p, h1, h2, h3 { color: white !important; }
    /* Fix za gumbe da budu uočljivi */
    .stButton button { border: 2px solid #ff4b4b !important; }
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
ja = st.text_input("👤 Unesi ime:", value="Nike").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
# Trajno čišćenje duplikata koji su zalijepljeni
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. BROJČANIK (VERZIJA KOJA SE MORA VIDJETI) ---
st.write("---")
# Koristimo warning i info okvire jer oni imaju fiksne boje koje pozadina ne može "pojest"
c1, c2 = st.columns(2)
with c1:
    st.warning(f"📖 Zalijepljeno: {len(moj_data['album'])}/458")
with c2:
    st.info(f"📦 Paketići: {moj_data['paketi']}")

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
            # Putanja do tvojih slika
            f = "slike/"
            path = f"{f}TN_ZG_EXT_{br}.jpeg" if br <= 75 else f"{f}TN_ZG_LEX_{br}.jpeg" 
            if os.path.exists(path):
                st.image(path, use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}", use_container_width=True):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. ALBUM (SADA SIGURAN) ---
st.subheader("📖 Pregled Albuma")
opcije = [f"{i}-{min(i+14, 458)}" for i in range(1, 459, 15)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

for r in range(3):
    cols = st.columns(5)
    for c in range(5):
        idx = start + (r * 5) + c
        if idx <= end:
            with cols[c]:
                if idx in moj_data["album"]:
                    # Ako je slika tu, prikaži ju
                    path = f"slike/TN_ZG_LEX_{idx}.jpeg" # Prilagodi putanju
                    if os.path.exists(path):
                        st.image(path, caption=f"Br. {idx}", use_container_width=True)
                    else:
                        st.success(f"Zalijepljeno #{idx}")
                else:
                    # Prazno mjesto je sada uočljiv crveni tekst
                    st.error(f"❌ Fali #{idx}")
