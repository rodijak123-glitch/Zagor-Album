# --- POPRAVLJENA FUNKCIJA ZA PDF (Bez kvačica da ne puca) ---
def generiraj_pdf_album(korisnik_ime, lista_slicica):
    # Kreiramo PDF
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Sigurnosno čišćenje imena od kvačica za PDF
    ime_safe = korisnik_ime.replace('č','c').replace('ć','c').replace('ž','z').replace('š','s').replace('đ','dj').replace('Č','C').replace('Ć','C').replace('Ž','Z').replace('Š','S').replace('Đ','Dj')

    # 1. Naslovnica
    if os.path.exists('image_4540f7.jpg'):
        pdf.image('image_4540f7.jpg', x=10, y=10, w=190)
    
    pdf.set_font("helvetica", "B", 24)
    pdf.set_y(220)
    pdf.set_text_color(255, 75, 75)
    pdf.cell(0, 15, "DIGITALNI ALBUM", align='C', ln=1)
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(0, 0, 0)
    # Koristimo ime_safe
    pdf.cell(0, 10, f"Vlasnik: {ime_safe}", align='C', ln=1)
    
    pdf.set_font("helvetica", "I", 12)
    pdf.cell(0, 10, f"Popunjen: {datetime.now().strftime('%d.%m.%Y.')}", align='C', ln=1)

    # 2. Stranice sa sličicama
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    # Ovdje smo maknuli "č" iz "sličica" -> "slicica"
    pdf.cell(0, 10, "Popis slicica u albumu", ln=1, align='C')
    pdf.ln(5)

    x_start, y_start = 10, 30
    thumb_w, thumb_h = 35, 48
    cols, rows_per_page = 5, 4
    
    for i in range(1, 459):
        idx = i - 1
        page_idx = idx % (cols * rows_per_page)
        col = page_idx % cols
        row = page_idx // cols
        
        if idx > 0 and page_idx == 0:
            pdf.add_page()
            
        cur_x = x_start + (col * (thumb_w + 3))
        cur_y = y_start + (row * (thumb_h + 8))
        
        if i in lista_slicica:
            path = get_file_path(i)
            if os.path.exists(path):
                pdf.image(path, x=cur_x, y=cur_y, w=thumb_w, h=thumb_h)
            else:
                pdf.rect(cur_x, cur_y, thumb_w, thumb_h)
        else:
            pdf.rect(cur_x, cur_y, thumb_w, thumb_h)
            
        pdf.set_xy(cur_x, cur_y + thumb_h + 1)
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(thumb_w, 4, f"Br. {i}", align='C')

    return pdf.output()

# --- DIO KODA KOD POBJEDE ---
if je_popunjen:
    import streamlit.components.v1 as components
    components.html('''
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
        </script>
    ''', height=1)

    st.markdown(f'<div class="winner-msg">🏅 BRAVO {ja.upper()}, ALBUM JE POPUNJEN! 🏅</div>', unsafe_allow_html=True)
    if os.path.exists('image_4540f7.jpg'):
        st.image('image_4540f7.jpg', use_container_width=True)
    
    st.divider()
    st.subheader("🎉 Tvoj osobni popunjeni album 🎉")
    
    with st.spinner("Stvaram PDF bez kvačica radi stabilnosti..."):
        try:
            pdf_out = generiraj_pdf_album(ja, moj_data["album"])
            st.download_button(
                label="📥 SKINI ALBUM U PDF-u",
                data=bytes(pdf_out),
                file_name=f"Zagor_Album_{ja}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Greška: {e}")

    if not st.checkbox("Prikaži sučelje za razmjenu"):
        st.stop()
