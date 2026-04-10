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

# POZADINA I FIX ZA VIDLJIVOST
bg_data = get_base64('image_50927d.jpg')
st.markdown(f'''
<style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("data:image/jpeg;base64,{bg_data}");
        background-size: cover; background-attachment: fixed;
    }}
    /* Forsiramo bijelu boju za sav tekst da ne nestane u mraku */
    .stMarkdown, p, h1, h2, h3, span, label {{ color: white !important; font-weight: bold; }}
    .stButton button {{ background-color: #ff4b4b !important; color: white !important; border-radius: 10px; }}
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

# --- 3. KORISNIK I ČIŠĆENJE ---
st.title("🛡️ Zagor Digitalni Album")
ja = st.text_input("👤 Unesi svoje ime za ulaz:", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]
# Trajno rješenje za broj 413
moj_data["duplikati"] = [d for d in moj_data.get("duplikati", []) if d not in moj_data.get("album", [])]

# --- 4. BROJČANIK (SADA ĆEŠ GA VIDJETI) ---
st.divider()
# Stavljamo statistiku u veliki Header koji ne može biti odrezan
st.subheader(f"📊 Zalijepljeno: {len(moj_data['album'])}/458 | 📦 Paketići: {moj_data['paketi']}")

if st.button("🎁 OTVORI NOVI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        moj_data["u_ruci"] = random.sample(range(1, 459), 5)
        spremi_u_bazu(baza)
        st.rerun()

# --- 5. LIJEPLJENJE ---
if moj_data.get("u_ruci"):
    st.write("### 📥 Nove sličice u ruci:")
    ruka_cols = st.columns(5)
    for i, br in enumerate(list(moj_data["u_ruci"])):
        with ruka_cols[i]:
            st.image(get_file_path(br), use_container_width=True)
            if st.button(f"Zalijepi #{br}", key=f"s_{br}_{i}", use_container_width=True):
                if br in moj_data["album"]:
                    if br not in moj_data["duplikati"]: moj_data["duplikati"].append(br)
                else:
                    moj_data["album"].append(br)
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 6. TRŽNICA ---
t1, t2 = st.tabs(["🔄 Tržnica", "📩 Ponude"])
with t1:
    ostali = [k for k in baza.keys() if k != ja]
    for k in ostali:
        njegovi = set(baza[k].get("duplikati", []))
        interes = njegovi.intersection(set(range(1, 459)) - set(moj_data["album"]))
        if interes:
            st.write(f"💡 **{k}** ima duplikate koji ti fale: `{list(interes)}`")
            d = st.multiselect(f"Što nudiš igraču {k}?", moj_data["duplikati"], key=f"d_{k}")
            t = st.multiselect(f"Što tražiš od njega?", list(interes), key=f"u_{k}")
            if st.button(f"Pošalji ponudu - {k}", key=f"b_{k}"):
                if d and t:
                    baza[k]["ponude"].append({"od": ja, "nudi": d, "trazi": t})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")

with t2:
    if not moj_data.get("ponude"): st.write("Nemaš novih ponuda.")
    for idx, p in enumerate(list(moj_data.get("ponude", []))):
        st.warning(f"📩 **{p['od']}** ti nudi {p['nudi']} za tvoje {p['trazi']}")
        if st.button("✅ Prihvati razmjenu", key=f"acc_{idx}"):
            for s in p["nudi"]:
                if s not in moj_data["album"]: moj_data["album"].append(s)
                if s in baza[p['od']]["duplikati"]: baza[p['od']]["duplikati"].remove(s)
            for s in p["trazi"]:
                if s not in baza[p['od']]["album"]: baza[p['od']]["album"].append(s)
                if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
            moj_data["ponude"].pop(idx)
            spremi_u_bazu(baza)
            st.rerun()

st.divider()

# --- 7. ALBUM (BEZ HTML-A, BEZ REZANJA) ---
st.subheader("📖 Pregled Albuma")
broj_po_stranici = 15
opcije = [f"{i}-{min(i+14, 458)}" for i in range(1, 459, broj_po_stranici)]
izabrano = st.select_slider("Odaberi stranicu:", options=opcije)
start, end = map(int, izabrano.split("-"))

# Koristimo izvorne Streamlit stupce umjesto HTML-a da izbjegnemo rezanje rubova
album_cols = st.columns(5)
for i in range(start, end + 1):
    col_idx = (i - start) % 5
    with album_cols[col_idx]:
        if i in moj_data["album"]:
            st.image(get_file_path(i), caption=f"Br. {i}", use_container_width=True)
        else:
            # Prazno mjesto koje se prilagođava širini
            st.markdown(f'''
            <div style="aspect-ratio: 3/4; background: rgba(255,255,255,0.05); border: 1px solid #444; 
            border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #555;">
                #{i}
            </div>
            <p style="text-align:center; font-size:12px;">Fali #{i}</p>
            ''', unsafe_allow_html=True)
