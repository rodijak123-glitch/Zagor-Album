import streamlit as st
import random
import os
import base64
import json
from datetime import datetime, timedelta

# --- 1. OSNOVNA KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Digitalni Album", layout="wide")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg"
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"

# --- 2. RAD S BAZOM ---
DB_FILE = "album_baza.json"
def ucitaj_bazu():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def spremi_u_bazu(baza_data):
    with open(DB_FILE, "w") as f: json.dump(baza_data, f)

baza = ucitaj_bazu()

# --- 3. KORISNIČKI PROFIL ---
st.title("🛡️ Zagor: Digitalni Album")
ja = st.text_input("👤 Prijavi se (Ime):", value="Gost").strip()

if ja not in baza:
    baza[ja] = {"album": [], "duplikati": [], "paketi": 10, "vrijeme": str(datetime.now()), "ponude": [], "u_ruci": []}
    spremi_u_bazu(baza)

moj_data = baza[ja]

# FIX: Osiguravanje da svi ključevi postoje kako bi izbjegli KeyError
for kljuc in ["album", "duplikati", "ponude", "u_ruci"]:
    if kljuc not in moj_data or not isinstance(moj_data[kljuc], list):
        moj_data[kljuc] = []

# --- 4. TAJMER I PAKETI ---
zadnje_vrijeme = datetime.fromisoformat(str(moj_data.get("vrijeme", datetime.now())))
if (datetime.now() - zadnje_vrijeme).total_seconds() > 1800:
    moj_data["paketi"] += 2
    moj_data["vrijeme"] = str(datetime.now())
    spremi_u_bazu(baza)

# --- 5. BROJČANICI (Stabilni prikaz) ---
metric_col1, metric_col2, metric_col3 = st.columns([1, 1, 2])
metric_col1.metric("Zalijepljeno", f"{len(moj_data['album'])}/458")
metric_col2.metric("Dostupni paketi", moj_data["paketi"])

if metric_col3.button("📦 OTVORI PAKETIĆ", use_container_width=True):
    if moj_data["paketi"] > 0 and not moj_data["u_ruci"]:
        moj_data["paketi"] -= 1
        novi_set = []
        while len(novi_set) < 5:
            r = random.randint(1, 458)
            if r not in novi_set: novi_set.append(r)
        moj_data["u_ruci"] = novi_set
        spremi_u_bazu(baza)
        st.rerun()

# --- 6. LIJEPLJENJE ---
if moj_data["u_ruci"]:
    st.write("---")
    cols = st.columns(5)
    za_brisanje = None
    for i, br in enumerate(moj_data["u_ruci"]):
        with cols[i]:
            st.image(get_file_path(br))
            if st.button(f"Zalijepi #{br}", key=f"btn_stick_{br}_{i}"):
                if br in moj_data["album"]:
                    moj_data["duplikati"].append(br)
                    st.toast(f"Duplikat #{br}")
                else:
                    moj_data["album"].append(br)
                    st.toast(f"Zalijepljeno #{br}")
                moj_data["u_ruci"].remove(br)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 7. TRŽNICA (S potpunim čišćenjem nakon razmjene) ---
st.header("🔄 Tržnica Sličica")
tab_razmjena, tab_moje = st.tabs(["Dostupne razmjene", "Moje ponude/Sandučić"])

with tab_razmjena:
    ostali = [k for k in baza.keys() if k != ja]
    for k in ostali:
        njegovi_dupli = set(baza[k].get("duplikati", []))
        meni_fale = set(range(1, 459)) - set(moj_data["album"])
        ponuda_interes = njegovi_dupli.intersection(meni_fale)
        
        if ponuda_interes:
            st.info(f"💡 **{k}** ima sličice koje ti trebaju: `{list(ponuda_interes)}`")
            dajem = st.multiselect(f"Tvoji duplikati za {k}:", moj_data["duplikati"], key=f"tr_off_{k}")
            trazim = st.multiselect(f"Što uzimaš od {k}?", list(ponuda_interes), key=f"tr_want_{k}")
            if st.button(f"Pošalji ponudu igraču {k}", key=f"send_{k}"):
                if dajem and trazim:
                    baza[k]["ponude"].append({"od": ja, "nudi": dajem, "trazi": trazim})
                    spremi_u_bazu(baza)
                    st.success("Ponuda poslana!")
                else:
                    st.warning("Odaberi sličice!")

with tab_moje:
    # Prikazujemo ponude koje su stigle TEBI
    if not moj_data["ponude"]:
        st.write("Nemaš novih ponuda.")
    else:
        for idx, p in enumerate(moj_data["ponude"]):
            st.warning(f"📩 **{p['od']}** ti nudi {p['nudi']} za tvoje {p['trazi']}")
            c_acc, c_rej = st.columns(2)
            if c_acc.button("✅ Prihvati", key=f"acc_{idx}_{ja}"):
                partner = p['od']
                # 1. Ja dobivam, on gubi
                for s in p["nudi"]:
                    if s not in moj_data["album"]: moj_data["album"].append(s)
                    if s in baza[partner]["duplikati"]: baza[partner]["duplikati"].remove(s)
                # 2. On dobiva, ja gubim
                for s in p["trazi"]:
                    if s not in baza[partner]["album"]: baza[partner]["album"].append(s)
                    if s in moj_data["duplikati"]: moj_data["duplikati"].remove(s)
                
                # 3. Čišćenje ponude
                moj_data["ponude"].pop(idx)
                spremi_u_bazu(baza)
                st.rerun()
            if c_rej.button("❌ Odbij", key=f"rej_{idx}_{ja}"):
                moj_data["ponude"].pop(idx)
                spremi_u_bazu(baza)
                st.rerun()

st.divider()

# --- 8. ALBUM ---
opcije = [f"{i}-{min(i+19, 458)}" for i in range(1, 459, 20)]
izabrano = st.select_slider("Stranica:", options=opcije)
start, end = map(int, izabrano.split("-"))

grid_html = ""
for i in range(start, end + 1):
    if i in moj_data["album"]:
        img_b64 = get_base64(get_file_path(i))
        content = f'<img src="data:image/jpeg;base64,{img_b64}" style="width:130px; border-radius:8px;">'
    else:
        content = f'<div style="width:130px; height:180px; background:#222; border:1px solid #444; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#555;">#{i}</div>'
    grid_html += f'<div style="text-align:center;">{content}</div>'

import streamlit.components.v1 as components
components.html(f'<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 15px; justify-items:center;">{grid_html}</div>', height=800)
