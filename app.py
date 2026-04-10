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

# FIKSNA POZADINA I STIL
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed; color: white;
    }}
    .custom-metric {{
        background: rgba(255, 75, 75, 0.2);
        padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b;
        text-align: center; margin-bottom: 20px;
    }}
</style>
''', unsafe_allow_html=True)

def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 2. BAZA PODATAKA ---
DB_FILE = "album_baza.json"
def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}

def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. KORISNIK I ČIŠĆENJE ---
st.title("🛡️ Zagor: Burza Sličica")
ja = st.text_input("Ime kolekcionara:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data: moj_data[k] = []

# AUTOMATSKO ČIŠĆENJE DUPLIKATA KOJI SU VEĆ ZALIJEPLJENI
# Ako je 413 u albumu, makni ga iz duplikata odmah!
moj_data["duplikati"] = [d for d in moj_data["duplikati"] if d not in moj_data["album"]]

# --- 4. NOVI BROJČANICI (HTML) ---
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    st.markdown(f'<div class="custom-metric">贴 Zalijepljeno<br><b style="font-size:25px;">{len(moj_data["album"])}/458</b></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="custom-metric">📦 Paketići<br><b style="font-size:25px;">{moj_data["paketi"]}</b></div>', unsafe_allow_html=True)
with col3:
    if st.button("📦 OTVORI PAKETIĆ", use_container_width=True, height=70):
        if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
            moj_data["paketi"] -= 1
            moj_data["u_ruci"] = random.sample(range(1, 459), 5)
            spremi_u_bazu(baza)
            st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data["u_ruci"]:
    st.write("---")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}"):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. TRŽNICA ---
t1, t2 = st.tabs(["Dostupne razmjene", "Moje ponude"])
with t1:
    ostali = [k for k in baza.keys() if k != ja]
    for k in ostali:
        njegovi_dupli = set(baza[k].get("duplikati", []))
        fale_meni = set(range(1, 459)) - set(moj_data["album"])
        interes = njegovi_dupli.intersection(fale_meni)
        if interes:
            st.info(f"💡 **{k}** nudi: `{list(interes)}`")
            dajem = st.multiselect(f"Tvoji duplikati za {k}:", moj_data["duplikati"], key=f"d_{k}")
            trazim = st.multiselect(f"Što uzimaš?", list(interes), key=f"u_{k}")
            if st.button(f"Pošalji ponudu - {k}", key=f"b_{k}"):
                if dajem and trazim:
                    baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")

with t2:
    for idx, p in enumerate(list(moj_data["ponude"])):
        st.warning(f"📩 **{p['od']}** nudi {p['nudi']} za {p['trazi']}")
        if st.button("✅ Prihvati", key=f"acc_{idx}"):
            partner = p['od']
            for s in p["nudi"]:
                if s not in moj_data["album"]: moj_data["album"].append(s)
                if s in baza[partner]["duplikati"]: baza[partner]["duplikati"].remove(s)
            for s in p["trazi"]:
                if s not in baza[partner]["album"]: baza[partner]["album"].append(s)
                if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
            moj_data["ponude"].pop(idx)
            spremi_u_bazu(baza)
            st.rerun()

st.divider()

# --- 7. ALBUM (S POPRAVLJENOM VISINOM I VELIČINOM) ---
st.subheader("📖 Tvoj Album")
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = '<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 20px; justify-items:center; padding-bottom: 50px;">'
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:160px; border-radius:10px; border: 2px solid #ff4b4b;">'
    else:
        content = f'<div style="width:160px; height:220px; background:rgba(0,0,0,0.5); border:1px solid #555; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#888;">Fali #{i}</div>'
    grid_html += f'<div>{content}<div style="color:white; text-align:center; margin-top:5px; font-weight:bold;">Br. {i}</div></div>'
grid_html += '</div>'

import streamlit.components.v1 as components
# VISINA POVEĆANA NA 1200 DA NIŠTA NE BUDE ODREZANO
components.html(grid_html, height=1200, scrolling=False)
