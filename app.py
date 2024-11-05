import streamlit as st
import hashlib
from process.utliss import is_encrypted
from process.imageProc import encyImage, decyImage
from process.fileProc import encyFile, decyFile
import process.textProc as te
import sqlite3
import process.textProc as te

conn = sqlite3.connect('users.db')
# Fungsi untuk mengenkripsi password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Fungsi untuk menampilkan aplikasi utama
def main_app():
    # ============= KONFIGURASI APLIKASI =============
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
            
            if not is_enc:
                st.image(file_data, caption="Gambar Asli", use_column_width=True)
            else:
                st.info("File terenkripsi terdeteksi. Gunakan key yang sesuai untuk mendekripsi.")
            
            key = st.text_input("Masukkan Key (angka)", type="password")
            col1, col2 = st.columns(2)
            
            with col1:
                encyImage(key, is_enc, file_data, upload_image)

            with col2:
                decyImage(key, file_data, upload_image)

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
        st.header("Super Encryption Text dengan Caesar, Vigenere, RC4, dan AES-ECB")
        input_text = st.text_area("Masukkan Text", height=100)
        key = st.number_input("Masukkan Key caesar", min_value=1, max_value=25, value=3)
        te.VIGENERE_KEY = st.text_input("Masukkan Key Vigenere", type="password")
        te.RC4_KEY = st.text_input("Masukkan Key RC4", type="password")
        te.AES_KEY = st.text_input("Masukkan Key AES", type="password")

        col1, col2 = st.columns(2)
        
        try:
            with col1:
                if st.button("🔒 Enkripsi"):
                    if input_text:
                        result = te.super_encrypt(input_text, key)
                        st.text_area("Hasil Enkripsi", result, height=100)
                    else:
                        st.error("Masukkan text yang akan dienkripsi")

            with col2:
                if st.button("🔓 Dekripsi"):
                    if input_text:
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

def main():
    st.set_page_config(page_title="Enkripsi App", page_icon="🔒")
    
    # Tambahkan CSS kustom
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        .stForm {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .viewerBadge_container__1QSob {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Tampilkan login form atau aplikasi utama
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🔒 Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    verify_credentials = conn.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{hash_password(password)}'").fetchone()
                    if verify_credentials:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = verify_credentials[3]
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Username atau password salah!")
    else:
        # Tampilkan sidebar dengan informasi user dan tombol logout
        with st.sidebar:
            # st.write(f"👤 User: {st.session_state.username}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
                # rerun untuk menghapus session state
        
        # Tampilkan aplikasi utama
        main_app()

if __name__ == "__main__":
    main()