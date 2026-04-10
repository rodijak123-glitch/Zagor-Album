import streamlit as st
import random
import time
from datetime import datetime, timedelta
from PIL import Image
import os

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(
    page_title="Zagor Digitalni Album | Zagor Te-Nay",
    page_icon="🪓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KONFIGURACIJA ALBUMA ---
UKUPNO_SLICICA = 385
SLICICA_U_PAKETU = 4
POCETNI_PAKETI = 5
PAKETI_REFILL_KOMADA = 2
REFILL_INTERVAL_MINUTA = 30
BASE_IMAGE_URL = "https://www.stripovi.com/covers/" # Osnovni URL za Ludens izdanja

# --- FUNKCIJE ---

# Funkcija za generiranje linka slike sa stripovi.com (Ludens Zagor_LEX)
def get_zagor_image_url(broj):
    # Formatira broj u 3 znamenke (npr. 1 -> 001, 23 -> 023)
    broj_str = str(broj).zfill(3)
    # Sklapa puni URL: Zagor_LEX_001.jpg
    puni_url = f"{BASE_IMAGE_URL}Zagor_LEX_{broj_str}.jpg"
    return puni_url

# Inicijalizacija stanja aplikacije (Session State)
def inicijaliziraj_stanje():
    if 'album' not in st.session_state:
        st.session_state.album = {}  # Format: {broj_slicice: kolicina}
        st.session_state.paketi_na_raspolaganju = POCETNI_PAKETI
        st.session_state.zadnji_refill = datetime.now()
        st.session_state.prikazi_balloons = False

# Logika za dodavanje novih paketića svakih 30 minuta
def provjeri_i_dodaj_pakete():
    trenutno_vrijeme = datetime.now()
    prolo_vremena = trenutno_vrijeme - st.session_state.zadnji_refill
    
    # Izračun koliko je intervala od 30 min prošlo
    broj_intervala = int(prolo_vremena.total_seconds() // (REFILL_INTERVAL_MINUTA * 60))
    
    if broj_intervala > 0:
        dodatni_paketi = broj_intervala * PAKETI_REFILL_KOMADA
        st.session_state.paketi_na_raspolaganju += dodatni_paketi
        # Postavlja zadnji refill na točno vrijeme zadnjeg procesiranog intervala
        st.session_state.zadnji_refill += timedelta(minutes=broj_intervala * REFILL_INTERVAL_MINUTA)
        return True
    return False

# --- POKRETANJE INICIJALIZACIJE ---
inicijaliziraj_stanje()
novi_paketi_dodani = provjeri_i_dodaj_pakete()

# --- CSS STILIZACIJA (Za ljepši izgled) ---
st.markdown("""
    <style>
    /* Stil za glavnu naslovnu sliku */
    .naslovna-slika {
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.7);
        margin-bottom: 20px;
    }
    /* Stil za gumb za otvaranje paketića */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        height: 3.5em;
        background-color: #e63946; /* Crvena boja Zagorovog znaka */
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-
