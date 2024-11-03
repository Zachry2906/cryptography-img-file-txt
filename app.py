import streamlit as st
from utliss import is_encrypted
from imageProc import encyImage, decyImage
from fileProc import encyFile, decyFile
import textProc as te


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
    st.header("Enkripsi Text")
    
    encryption_method = st.selectbox(
        "Pilih Metode Enkripsi",
        ["Caesar", "Vigenere", "RC4", "Block ECB", "Super Encryption"]
    )
    
    input_text = st.text_area("Masukkan Text", height=100)
    
    if encryption_method == "Caesar":
        key = st.number_input("Masukkan Key (angka)", min_value=1, max_value=25, value=3)
    elif encryption_method in ["Vigenere", "RC4", "Block ECB"]:
        key = st.text_input("Masukkan Key", type="password")
    else:  # Super Encryption
        key = st.number_input("Masukkan Key (angka)", min_value=1, max_value=25, value=3)

    col1, col2 = st.columns(2)
    
    try:
        with col1:
            if st.button("🔒 Enkripsi"):
                if input_text:
                    result = None
                    if encryption_method == "Caesar":
                        result = te.caesar_encrypt(input_text, key)
                    elif encryption_method == "Vigenere":
                        result = te.vigenere_encrypt(input_text, key)
                    elif encryption_method == "RC4":
                        result = te.rc4_encrypt(input_text, key)
                    elif encryption_method == "Block ECB":
                        result = te.block_ecb_encrypt(input_text, key)
                    else:  # Super Encryption
                        result = te.super_encrypt(input_text, key)
                    
                    st.text_area("Hasil Enkripsi", result, height=100)
                else:
                    st.error("Masukkan text yang akan dienkripsi")

        with col2:
            if st.button("🔓 Dekripsi"):
                if input_text:
                    result = None
                    if encryption_method == "Caesar":
                        result = te.caesar_decrypt(input_text, key)
                    elif encryption_method == "Vigenere":
                        result = te.vigenere_decrypt(input_text, key)
                    elif encryption_method == "RC4":
                        result = te.rc4_decrypt(input_text, key)
                    elif encryption_method == "Block ECB":
                        result = te.block_ecb_decrypt(input_text, key)
                    else:  # Super Encryption
                        result = te.super_decrypt(input_text, key)
                    
                    st.text_area("Hasil Dekripsi", result, height=100)
                else:
                    st.error("Masukkan text yang akan didekripsi")
                    
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        
    with st.expander("ℹ️ Informasi Metode Enkripsi"):
        st.markdown("""
        - **Caesar**: Menggeser setiap huruf sesuai key (1-25)
        - **Vigenere**: Menggunakan kata kunci untuk menggeser huruf
        - **RC4**: Stream cipher dengan key string
        - **Block ECB**: Block cipher menggunakan AES-ECB
        - **Super Encryption**: Kombinasi Caesar + Vigenere + RC4 + Block ECB
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