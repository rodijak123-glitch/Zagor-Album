import streamlit as st
import random
import os
import json

# --- 1. POSTAVKE (BEZ KOMPLICIRANOG CSS-A) ---
st.set_page_config(page_title="Zagor Album", layout="wide")

# Samo osnovna tamna tema koja neće sakriti tekst
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# --- 2. LOGIKA ZA SLIKE I BAZU ---
def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

DB_FILE = "album_baza.json"
def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. KORISNIK ---
st.title("🛡️ Zagor Digitalni Album")
ja = st.text_input("👤 Prijavi se:", value="Nike").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# FIX ZA DUPLIKATE (Automatski briše zalijepljene iz ponude)
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. BROJČANIK (OBIČAN TEKST KOJI SE MORA VIDJETI) ---
st.divider()
# Koristimo st.write umjesto subheadera jer je on najotporniji na nestajanje
st.write(f"### 📖 Zalijepljeno: **{len(moj_data['album'])} / 458**")
st.write(f"### 📦 Imaš paketića: **{moj_data['paketi']}**")

if st.button("🎁 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        moj_data["u_ruci"] = random.sample(range(1, 459), 5)
        spremi_u_bazu(baza)
        st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data.get("u_ruci"):
    st.info("📥 Nove sličice u ruci - klikni za ljepljenje u album:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            path = get_file_path(br)
            if os.path.exists(path):
                st.image(path, use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}"):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. ALBUM (ČISTI PREGLED) ---
st.subheader("📖 Pregled tvojih sličica")
izbor = st.select_slider("Pomakni stranicu:", options=[f"{i}-{min(i+14, 458)}" for i in range(1, 459, 15)])
start, end = map(int, izbor.split("-"))

for r in range(3):
    cols = st.columns(5)
    for c in range(5):
        br = start + (r * 5) + c
        if br <= end:
            with cols[c]:
                if br in moj_data["album"]:
                    st.image(get_file_path(br), caption=f"Zalijepljeno #{br}", use_container_width=True)
                else:
                    # Samo jednostavna oznaka, bez HTML-a koji bi mogao 'puknuti'
                    st.write(f"❌ **Fali #{br}**")
