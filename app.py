import streamlit as st
import random
import os
import json

# --- 1. SAMO OSNOVNO (BEZ CSS-A KOJI KVARI OKVIRE) ---
st.set_page_config(page_title="Zagor Album", layout="wide")

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
ja = st.text_input("👤 Prijavi se:", value="Nike").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "u_ruci": [], "brojac_do_paketa": 0}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# --- 3. TVOJ PRAVI BROJČANIK (ZA NOVI PAKET) ---
# Svakih 10 zalijepljenih sličica = 1 novi paket
napredak = moj_data.get("brojac_do_paketa", 0)
st.write(f"### 🎯 Do sljedećeg paketića fali još: **{10 - napredak}** zalijepljenih sličica")
st.progress(napredak / 10)

if napredak >= 10:
    moj_data["paketi"] += 1
    moj_data["brojac_do_paketa"] = 0
    spremi_u_bazu(baza)
    st.balloons()
    st.success("Dobio si GRATIS paket!")
    st.rerun()

# --- 4. AKCIJE ---
st.write(f"📦 Paketića na zalihi: **{moj_data['paketi']}**")
if st.button("🎁 OTVORI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        moj_data["u_ruci"] = random.sample(range(1, 459), 5)
        spremi_u_bazu(baza)
        st.rerun()

# --- 5. LIJEPLJENJE (S POPRAVKOM BROJČANIKA) ---
if moj_data.get("u_ruci"):
    st.write("### 📥 Sličice u ruci:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            path = get_file_path(br)
            if os.path.exists(path):
                st.image(path, use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}"):
                if br not in moj_data["album"]:
                    moj_data["album"].append(br)
                    # Povećavamo brojčanik samo za nove sličice
                    moj_data["brojac_do_paketa"] = moj_data.get("brojac_do_paketa", 0) + 1
                else:
                    moj_data["duplikati"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. ALBUM (BEZ DEFORMACIJA) ---
st.subheader("📖 Pregled Albuma")
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
                    # Običan tekst umjesto HTML-a da se ne deformira
                    st.write(f"⬜ **Fali #{br}**")
