import streamlit as st
import random
import os
import base64

# --- 1. KONFIGURACIJA ---
st.set_page_config(page_title="Zagor: Kolekcionar", layout="wide")

# --- 2. DEFINICIJA ---
UKUPNO_SLICICA = 458 
SLICICA_U_PAKETU = 5

# --- 3. POZADINA I FIKSIRANJE DIZAJNA ---
def apply_custom_styles(file_path):
    # CSS za fiksiranje albuma i skrivanje Streamlit zoom gumba
    style = f'''
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), url("data:image/jpeg;base64,{{data}}");
            background-size: cover; background-attachment: fixed;
        }}
        /* Skrivanje gumba za "otvori u novom tabu" iznad slika */
        button[title="View fullscreen"] {{
            display: none !important;
        }}
        /* FIKSNI KONTEJNER: sprečava deformaciju albuma */
        .slicica-slot {{
            height: 200px; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }}
        </style>
    '''
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            st.markdown(style.format(data=data), unsafe_allow_html=True)

# Postavljanje pozadine
apply_custom_styles('image_50927d.jpg')

# --- 4. STANJE APLIKACIJE ---
if 'album' not in st.session_state: st.session_state.album = {}      
if 'na_cekanju' not in st.session_state: st.session_state.na_cekanju = [] 
if 'paketi' not in st.session_state: st.session_state.paketi = 5

# --- 5. PUTANJE SLIKA ---
def get_file_path(broj):
    f = "slike/"
    if broj <= 75: return f"{f}TN_ZG_EXT_{broj}.jpeg"      #
    elif broj <= 385: return f"{f}TN_ZG_LEX_{broj}.jpeg"   #
    elif broj <= 431: return f"{f}TN_ZG_LUSP_{broj-385}.jpeg" #
    else: return f"{f}TN_ZG_LUCI_{broj-431}.jpeg"         #

# --- 6. SIDEBAR ---
with st.sidebar:
    st.header("👤 Kolekcija")
    sakupljeno = len(st.session_state.album)
    st.metric("Zalijepljeno", f"{sakupljeno} / {UKUPNO_SLICICA}")
    st.metric("Paketići", st.session_state.paketi)

# --- 7. NASLOV I OTVARANJE ---
st.markdown("<h1 style='text-align: center; color: #8B0000;'>Zagor: Digitalni Album</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("📦 OTVORI NOVI PAKETIĆ", use_container_width=True):
        if st.session_state.paketi > 0:
            st.session_state.paketi -= 1
            st.session_state.na_cekanju.extend([random.randint(1, UKUPNO_SLICICA) for _ in range(SLICICA_U_PAKETU)])
            st.rerun()

# --- 8. PROSTOR ZA LIJEPLJENJE ---
if st.session_state.na_cekanju:
    st.write("### 📥 Sličice u ruci:")
    cols_ruka = st.columns(5)
    for i, br in enumerate(st.session_state.na_cekanju[:10]):
        with cols_ruka[i % 5]:
            p = get_file_path(br)
            if os.path.exists(p): st.image(p, width=100)
            if st.button(f"Zalijepi #{br}", key=f"s_{i}_{br}"):
                st.session_state.album[br] = st.session_state.album.get(br, 0) + 1
                st.session_state.na_cekanju.pop(i)
                # Automatski skok na stranicu
                start_p = ((br - 1) // 20) * 20 + 1
                st.session_state.pregled_raspon = f"{start_p}-{min(start_p+19, UKUPNO_SLICICA)}"
                st.rerun()

# --- 9. PREGLED ALBUMA ---
st.divider()
options = [f"{i}-{min(i+19, UKUPNO_SLICICA)}" for i in range(1, UKUPNO_SLICICA + 1, 20)]
if 'pregled_raspon' not in st.session_state or st.session_state.pregled_raspon not in options:
    st.session_state.pregled_raspon = options[0]

izabrani = st.select_slider("Stranica:", options=options, value=st.session_state.pregled_raspon)
st.session_state.pregled_raspon = izabrani
start_br, end_br = map(int, izabrani.split("-"))

cols_album = st.columns(5)
for i in range(start_br, end_br + 1):
    with cols_album[(i - start_br) % 5]:
        # Omotač koji drži fiksnu visinu (slicica-slot)
        st.markdown('<div class="slicica-slot">', unsafe_allow_html=True)
        
        if i in st.session_state.album:
            putanja = get_file_path(i)
            if os.path.exists(putanja):
                # Sličica uvećana za 20% (fiksno width=120)
                st.image(putanja, width=120)
            else:
                st.write(f"Zalijepljeno #{i}")
        else:
            # Sivi prozirni pravokutnik (isto fiksne dimenzije)
            st.markdown(f'''
                <div style="height:160px; width:120px; border-radius:10px; 
                display:flex; align-items:center; justify-content:center; 
                color:#999; background: rgba(0,0,0,0.5); font-size: 11px;">
                Fali #{i}
                </div>
            ''', unsafe_allow_html=True)
            
        st.caption(f"Br. {i}")
        st.markdown('</div>', unsafe_allow_html=True)
