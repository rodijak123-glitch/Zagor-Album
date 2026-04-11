import streamlit as st
import json
import random
import os
import base64
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- 1. KONFIGURACIJA I POVEZIVANJE ---
st.set_page_config(page_title="Zagor Album: GitHub Baza", layout="wide")

# Dohvaćanje tajni iz Streamlit Secrets
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["REPO_NAME"]
except:
    st.error("Nedostaju GITHUB_TOKEN ili REPO_NAME u Secretsima!")
    st.stop()

FILE_PATH = "album_baza.json"

def ucitaj_iz_githuba():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode()
        return json.loads(content)
    return {}

def spremi_na_github(baza_data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Prvo moramo dobiti 'sha' trenutne datoteke da bismo je prepisali
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    
    # Pretvaramo bazu u JSON i onda u Base64
    novi_sadrzaj = json.dumps(baza_data, indent=4)
    encoded_content = base64.b64encode(novi_sadrzaj.encode()).decode()
    
    payload = {
        "message": f"Update baze: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": encoded_content
    }
    if sha:
        payload["sha"] = sha
        
    requests.put(url, headers=headers, json=payload)

# --- 2. DIZAJN I STIL ---
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

# --- 3. LOGIKA KORISNIKA ---
if 'baza' not in st.session_state:
    st.session_state.baza = ucitaj_iz_githuba()

st.title("🏹 Zagor: Digitalni Album (GitHub Database)")
ja = st.text_input("Unesi svoje ime:").strip()

if not ja:
    st.warning("Unesi ime za početak sakupljanja!")
    st.stop()

if ja not in st.session_state.baza:
    st.session_state.baza[ja] = {
        "album": [], "duplikati": [], "paketi": 10, 
        "ponude": [], "u_ruci": [], 
        "zadnji_gratis": str(datetime.now() - timedelta(minutes=30))
    }
    spremi_na_github(st.session_state.baza)

moj_data = st.session_state.baza[ja]

# Osiguranje da svi ključevi postoje (za stare baze)
za_provjeru = ["album", "duplikati", "ponude", "u_ruci"]
for k in za_provjeru:
    if k not in moj_data: moj_data[k] = []

# --- 4. BROJČANICI I TIMER ---
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
        st.markdown(f'<div class="metric-box">⌛ Novi paketi za:<br><span style="font-size:25px;">{m:02d}:{s:02d}</span></div>', unsafe_allow_html=True)
    else:
        if st.button("🎁 PREUZMI 2 GRATIS PAKETA", use_container_width=True):
            moj_data["paketi"] += 2
            moj_data["zadnji_gratis"] = str(datetime.now())
            spremi_na_github(st.session_state.baza)
            st.rerun()

    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if moj_data["paketi"] > 0 and not moj_data.get("u_ruci"):
            moj_data["paketi"] -= 1
            moj_data["u_ruci"] = random.sample(range(1, 459), 5)
            spremi_na_github(st.session_state.baza)
            st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data.get("u_ruci"):
    st.write("---")
    st.subheader("Novi paket sadrži:")
    cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"z_{br}_{i}"):
                if br in moj_data["album"]:
                    if br not in moj_data["duplikati"]:
                        moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_na_github(st.session_state.baza)
                st.rerun()

# --- 6. TRŽNICA ---
st.divider()
t1, t2 = st.tabs(["🤝 Razmjene", "📩 Sandučić"])

with t1:
    ostali = [k for k in st.session_state.baza.keys() if k != ja]
    found = False
    for k in ostali:
        njegovi_dupli = set(st.session_state.baza[k].get("duplikati", []))
        fale_meni = set(range(1, 459)) - set(moj_data["album"])
        interes = njegovi_dupli.intersection(fale_meni)
        if interes:
            found = True
            st.info(f"💡 **{k}** ima sličice koje ti trebaju: `{list(interes)}`")
            dajem = st.multiselect(f"Što nudiš {k}?", moj_data["duplikati"], key=f"d_{k}")
            trazim = st.multiselect(f"Što želiš od {k}?", list(interes), key=f"u_{k}")
            if st.button(f"Pošalji ponudu - {k}", key=f"b_{k}"):
                if dajem and trazim:
                    if "ponude" not in st.session_state.baza[k]: st.session_state.baza[k]["ponude"] = []
                    st.session_state.baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim})
                    spremi_na_github(st.session_state.baza)
                    st.success("Ponuda poslana!")
    if not found:
        st.write("Trenutno nitko nema duplikate koji tebi fale.")

with t2:
    if not moj_data.get("ponude"):
        st.write("Nema novih ponuda u sandučiću.")
    else:
        for idx, p in enumerate(list(moj_data["ponude"])):
            st.warning(f"📩 **{p['od']}** ti nudi {p['nudi']} u zamjenu za tvoje {p['trazi']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Prihvati", key=f"acc_{idx}"):
                    partner = p['od']
                    # Meni dodaj, njemu makni
                    for s in p["nudi"]:
                        if s not in moj_data["album"]: moj_data["album"].append(s)
                        if s in st.session_state.baza[partner]["duplikati"]:
                            st.session_state.baza[partner]["duplikati"].remove(s)
                    # Njemu dodaj, meni makni
                    for s in p["trazi"]:
                        if s not in st.session_state.baza[partner]["album"]:
                            st.session_state.baza[partner]["album"].append(s)
                        if s in moj_data["duplikati"]:
                            moj_data["duplikati"].remove(s)
                    moj_data["ponude"].pop(idx)
                    spremi_na_github(st.session_state.baza)
                    st.rerun()
            with c2:
                if st.button("❌ Odbij", key=f"rej_{idx}"):
                    moj_data["ponude"].pop(idx)
                    spremi_na_github(st.session_state.baza)
                    st.rerun()

# --- 7. ALBUM GRID ---
st.divider()
st.subheader("📖 Pregled Albuma")
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

st.write("---")
st.caption("Sustav automatski sinkronizira bazu s GitHubom nakon svakog poteza.")
