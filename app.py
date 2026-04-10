import streamlit as st
import random
import os
import base64
import json
from datetime import datetime, timedelta

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor Album", layout="wide")

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
        text-align: center; margin-bottom: 10px; min-height: 80px;
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

# --- 3. KORISNIK ---
ja = st.text_input("Tvoje ime:", value="Nike").strip()
if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": [], "zadnji_gratis": str(datetime.now() - timedelta(minutes=30))}
    spremi_u_bazu(baza)

moj_data = baza[ja]
for k in ["album", "duplikati", "ponude", "u_ruci"]:
    if k not in moj_data: moj_data[k] = []
if "zadnji_gratis" not in moj_data:
    moj_data["zadnji_gratis"] = str(datetime.now() - timedelta(minutes=30))

# --- 4. BROJČANICI I FIX ZA TIMER ---
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
        # JS Timer ubačen direktno u metric-box stil (Sada s vidljivim ID-om)
        st.markdown(f"""
            <div class="metric-box" style="background: rgba(0,0,0,0.6); border-color: #ff4b4b;">
                ⌛ Novi paketi za:<br>
                <span id="countdown" style="font-size:30px; font-weight:bold; color: #ff4b4b;">--:--</span>
            </div>
            <script>
                var seconds = {sekundi_ostalo};
                var timer = setInterval(function() {{
                    var m = Math.floor(seconds / 60);
                    var s = seconds % 60;
                    document.getElementById("countdown").innerHTML = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
                    if (seconds <= 0) {{
                        clearInterval(timer);
                        window.parent.postMessage({{type: 'streamlit:setComponentValue', value: true}}, '*');
                        setTimeout(function() {{ window.location.reload(); }}, 500);
                    }}
                    seconds--;
                }}, 1000);
            </script>
        """, unsafe_allow_html=True)
    else:
        if st.button("🎁 PREUZMI 2 GRATIS PAKETA", use_container_width=True):
            moj_data["paketi"] += 2
            moj_data["zadnji_gratis"] = str(datetime.now())
            spremi_u_bazu(baza)
            st.rerun()

    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
            moj_data["paketi"] -= 1
            moj_data["u_ruci"] = random.sample(range(1, 459), 5)
            spremi_u_bazu(baza)
            st.rerun()

# --- 5. LIJEPLJENJE I TRŽNICA (Ostaje nepromijenjeno) ---
if moj_data["u_ruci"]:
    st.write("---")
    cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}"):
                if br not in moj_data["album"]: moj_data["album"].append(br)
                elif br not in moj_data["duplikati"]: moj_data["duplikati"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

# --- 6. ALBUM GRID (Smanjen height na 1050px za bolji fit) ---
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
# Postavljeno na 1050px kako bi se eliminirao prazan prostor uz zadržavanje punog prikaza
components.html(grid_html, height=1050)
