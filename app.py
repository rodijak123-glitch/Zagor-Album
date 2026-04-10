import streamlit as st
import random
import os
import json

# --- 1. POSTAVKE ---
st.set_page_config(page_title="Zagor Album", layout="wide")

# Isključivo osnovni stil za padding vrha
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# --- 2. BAZA I FUNKCIJE ---
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

# Trajno čišćenje duplikata koji su već u albumu
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. POVRATAK BROJČANIKA (Metrics) ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric("Zalijepljeno sličica", f"{len(moj_data['album'])} / 458")
with col2:
    st.metric("Preostalo paketića", moj_data['paketi'])

if st.button("🎁 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        moj_data["u_ruci"] = random.sample(range(1, 459), 5)
        spremi_u_bazu(baza)
        st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data.get("u_ruci"):
    st.write("### 📥 Nove sličice:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            path = get_file_path(br)
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

# --- 6. ALBUM (ČISTI I PREGLEDNI) ---
st.subheader("📖 Pregled Albuma (15 po stranici)")
izbor = st.select_slider("Stranica:", options=[f"{i}-{min(i+14, 458)}" for i in range(1, 459, 15)])
start, end = map(int, izbor.split("-"))

for r in range(3):
    cols = st.columns(5)
    for c in range(5):
        br = start + (r * 5) + c
        if br <= end:
            with cols[c]:
                if br in moj_data["album"]:
                    st.image(get_file_path(br), caption=f"Br. {br}", use_container_width=True)
                else:
                    # Povratak jednostavnog okvira koji drži visinu
                    st.markdown(f"""
                    <div style="height: 180px; background: #262730; border-radius: 10px; 
                    display: flex; align-items: center; justify-content: center; 
                    border: 1px solid #444; color: #888; font-weight: bold;">
                        #{br}
                    </div>
                    """, unsafe_allow_html=True)
