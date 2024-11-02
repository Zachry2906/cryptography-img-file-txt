import streamlit as st
from utliss import is_encrypted
from imageProc import encyImage, decyImage
from fileProc import encyFile, decyFile

# ============= KONFIGURASI APLIKASI =============
st.set_page_config(page_title="Enkripsi App", page_icon="🔒")
st.title("🔒 Aplikasi Enkripsi")
st.markdown("Enkripsi file dan gambar Anda dengan aman menggunakan berbagai metode enkripsi")
tab1, tab2, tab3 = st.tabs(["📸 Enkripsi Gambar", "📁 Enkripsi File", "📝 Enkripsi Text"])


# ============= TAB 1: ENKRIPSI GAMBAR =============
with tab1:
    st.header("Enkripsi Gambar dengan XOR")
    upload_image = st.file_uploader("Unggah gambar", type=["jpg", "png", "jpeg", "bmp"])

    if upload_image is not None:
        file_data = upload_image.read()
        is_enc = is_encrypted(file_data)
        
        # Tampilkan gambar asli jika bukan file terenkripsi
        if not is_enc:
            st.image(file_data, caption="Gambar Asli", use_column_width=True)
        else:
            st.info("File terenkripsi terdeteksi. Gunakan key yang sesuai untuk mendekripsi.")
        
        # Input key dan proses enkripsi/dekripsi
        key = st.text_input("Masukkan Key (angka)", type="password")
        col1, col2 = st.columns(2)
        
        with col1:
            encyImage(key, is_enc, file_data,upload_image)

        with col2:
            decyImage(key, file_data,upload_image)

# ============= TAB 2: ENKRIPSI FILE =============
with tab2:
    st.header("Enkripsi File dengan Fernet")
    mode = st.radio("Pilih Mode:", ("🔒 Enkripsi", "🔓 Dekripsi"))
    
    if mode == "🔒 Enkripsi":
        encyFile()
    else:
        decyFile()

# ============= TAB 3: TEXT =============
with tab3:
    st.header("Comming Soon")
    st.markdown("""
    """)

# ============= FOOTER =============
st.markdown("---")
hide_st_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .viewerBadge_container__1QSob {display: none;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)