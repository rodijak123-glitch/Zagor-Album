import streamlit as st
import os

# --- SKRIPTA ZA TOTALNI RESET ---
st.set_page_config(page_title="Reset Baze", layout="wide")

st.title("🗑️ Čišćenje sustava")

# Putanja do baze
DB_FILE = "album_baza.json"

if os.path.exists(DB_FILE):
    try:
        os.remove(DB_FILE)
        st.success(f"✅ Baza '{DB_FILE}' je uspješno obrisana!")
        st.info("Sada možeš vratiti glavni kod aplikacije na GitHub i krenuti ispočetka.")
    except Exception as e:
        st.error(f"Pokušao sam obrisati, ali se pojavila greška: {e}")
else:
    st.warning("⚠️ Baza nije pronađena. Moguće je da je već obrisana ili još nije kreirana.")

st.write("---")
st.write("Trenutne datoteke u mapi:")
st.write(os.listdir("."))
