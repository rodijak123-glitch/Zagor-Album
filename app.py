import streamlit as st
import random
import os
import json
from datetime import datetime

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album", layout="wide")

# CSS koji samo postavlja pozadinu, ne dira tekst
st.markdown(f'''
<style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url("https://wallpaperaccess.com/full/2454558.jpg");
        background-size: cover;
    }}
    .stMarkdown, p, h1, h2, h3 {{ color: white !important; }}
</style>
''', unsafe_allow_html=True)

def get_file_path(broj):
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

# --- 3. KORISNIK I FIX ZA 413 ---
st.title("🛡️ Zagor Digitalni Album")
ja = st.text_input("👤 Prijavi se:", value="Nike").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
# Čišćenje duplikata koji su već zalijepljeni
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. BROJČANIK (SADA NA GUMBIMA DA SE VIDI) ---
# Ako ti fali gornji brojčanik, on je sada dio navigacije
st.write("---")
col_stat1, col_stat2 = st.columns(2)
with col_stat1:
    st.button(f"📖 Zalijepljeno: {len(moj_data['album'])}/458", disabled=True, use_container_width=True)
with col_stat2:
    st.button(f"📦 Paketići: {moj_data['paketi']}", disabled=True, use_container_width=True)

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

# --- 6. ALBUM (SADA 100% VIDLJIV) ---
st.subheader("📖 Pregled Albuma")
opcije = [f"{i}-{min(i+14, 458)}" for i in range(1, 459, 15)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

# Crtanje albuma bez ikakvog HTML-a, samo st.columns i st.image
for r in range(3):
    cols = st.columns(5)
    for c in range(5):
        idx = start + (r * 5) + c
        if idx <= end:
            with cols[c]:
                if idx in moj_data["album"]:
                    # Ako je sličica zalijepljena, prikaži sliku
                    st.image(get_file_path(idx), caption=f"Br. {idx}", use_container_width=True)
                else:
                    # Ako fali, prikaži sivi gumb kao okvir koji se ne može pomicati
                    st.button(f"❌ Fali #{idx}", key=f"slot_{idx}", disabled=True, use_container_width=True)
