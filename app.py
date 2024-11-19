import streamlit as st
import hashlib
from process.utliss import is_encrypted
from process.imageProc import encyImage, decyImage, encyStegano, decyStegano
from process.fileProc import encyFile, decyFile
import process.textProc as te
import sqlite3
import pandas as pd
import base64
from io import BytesIO 
from PIL import Image

conn = sqlite3.connect('users.db')
# Fungsi untuk mengenkripsi password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def encode_message(message, image):
    encoded_image = image.copy()

    encoded_image.putdata(encode_data(image, message))

    encoded_image_path = "encoded.png"
    encoded_image.save(encoded_image_path)

    st.success("Image encoded successfully.")
    show_encoded_image(encoded_image_path)


def decode_message(image, key):
    decoded_message = decode_data(image)
    decripted_message = te.caesar_decrypt(decoded_message, key)
    return decripted_message


def encode_data(image, data):
    # Menambahkan delimiter '$' sebagai penanda akhir pesan
    data = data + "$"  
    
    # Mengkonversi pesan ke binary
    # Contoh: jika data = "Hi$", maka:
    # 'H' -> 01001000
    # 'i' -> 01101001
    # '$' -> 00100100
    # data_bin = "010010000110100100100100"
    data_bin = ''.join(format(ord(char), '08b') for char in data)

    # Mengambil semua pixel dari gambar
    pixels = list(image.getdata())
    encoded_pixels = []

    index = 0
    for pixel in pixels:
        if index < len(data_bin):
            # Mengambil nilai Red dari pixel (R,G,B)
            red_pixel = pixel[0]
            
            # Proses mengubah bit terakhir:
            # 1. red_pixel & 254 -> mengatur bit terakhir jadi 0
            #    Contoh: 10101111 & 11111110 = 10101110
            # 2. int(data_bin[index]) -> mengambil bit pesan (0 atau 1)
            # 3. | -> menyisipkan bit pesan ke bit terakhir
            #    Contoh: 10101110 | 1 = 10101111
            new_pixel = (red_pixel & 254) | int(data_bin[index])
            
            # Menyimpan pixel baru (R_new,G,B)
            encoded_pixels.append((new_pixel, pixel[1], pixel[2]))
            index += 1
        else:
            # Jika pesan sudah habis, pixel tidak dimodifikasi
            encoded_pixels.append(pixel)

    return encoded_pixels


def decode_data(image):
    # Mengambil semua pixel dari gambar
    pixels = list(image.getdata())
    
    # String untuk menyimpan binary hasil ekstraksi
    data_bin = ""
    
    # Mengekstrak bit LSB dari setiap pixel red
    for pixel in pixels:
        # bin(pixel[0])[-1] mengambil bit terakhir dari nilai Red
        # Contoh: bin(148) = "10010100" -> ambil "0"
        data_bin += bin(pixel[0])[-1]
    
    # String untuk menyimpan pesan hasil konversi
    data = ""
    
    # Konversi setiap 8 bit ke karakter
    for i in range(0, len(data_bin), 8):
        # Mengambil 8 bit
        byte = data_bin[i:i + 8]
        # Konversi 8 bit ke karakter
        # Contoh: "01001000" -> 72 -> "H"
        data += chr(int(byte, 2))
        # Berhenti jika menemukan delimiter '$'
        if data[-1] == "$":
            break
    
    # Mengembalikan pesan tanpa delimiter
    return data[:-1]


def show_encoded_image(image_path):
    encoded_image = Image.open(image_path)

    st.image(encoded_image, caption="Encoded Image", use_column_width=True)

    buffered = BytesIO()
    encoded_image.save(buffered, format="PNG")

    img_str = base64.b64encode(buffered.getvalue()).decode()

    href = ('<a href="data:file/png;base64,' + img_str + '" '
            'download="' + image_path + '">Download Encoded Image</a>')

    st.markdown(href, unsafe_allow_html=True)


# Fungsi untuk menampilkan aplikasi utama
def main_app():
    # ============= KONFIGURASI APLIKASI =============
    st.title("🏥 Sistem Keamanan Data Medis")
    st.markdown("Enkripsi data medis pasien dengan aman menggunakan berbagai metode enkripsi")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📸 Enkripsi Citra Medis", 
    "📸 Steganografi Dokumen", 
    "📁 Enkripsi Berkas Pasien", 
    "📝 Enkripsi Catatan Medis",
    "📈 Riwayat Enkripsi"
])

    # ============= TAB 1: ENKRIPSI GAMBAR =============
    with tab1:
        st.header("Enkripsi Citra Medis dengan XOR")
        upload_image = st.file_uploader("Unggah hasil pemindaian medis (X-Ray, MRI, USG)", type=["jpg", "png", "jpeg", "bmp"])

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

    # ============= TAB 2: STEGANOGRAFI GAMBAR =============
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.header("Penyembunyian Data Pasien dalam Citra Medis")
            pesan = st.text_input("Masukkan Data Rahasia Pasien")
            key = 3000
            # key = st.text_input("Masukkan Kunci", type="password", key='encode')
            # try :
            #     key = int(key)
            # except:
            #     st.error("Key harus berupa angka")
            message = te.caesar_encrypt(pesan, key)
            # password = col1.text_input("Enter Password", type="password")
            image_file = st.file_uploader("Pilih Gambar", type=["png", "jpg", "jpeg"])
        with col2:
            st.header("Citra Medis dengan Data Rahasia")
            if message and image_file:
                image = Image.open(image_file)
                encode_message(message, image)

        st.markdown("---")

        col3, col4 = st.columns(2)
        with col3:
            st.header("Ekstrak Data Rahasia dari Citra Medis")
            # keyDecy = st.text_input("Masukkan Kunci", type="password", key='decode')
        with col4:
            st.header("Data Rahasia Pasien")

        # decode_password = col3.text_input("Enter Password for Decoding", type="password")
        decode_image_file = col3.file_uploader(
            "Pilih Gambar yang Ingin diketahui pesannya", type=["png", "jpg", "jpeg"]
        )

        if decode_image_file:
            decode_image = Image.open(decode_image_file)
            col4.write("Pesan Rahasia: " + decode_message(decode_image, key))

    # ============= TAB 3: ENKRIPSI FILE =============
    with tab3:
        st.header("Enkripsi Berkas Rekam Medis dengan Fernet")
        mode = st.radio("Pilih Mode:", ("🔒 Enkripsi", "🔓 Dekripsi"))
        
        if mode == "🔒 Enkripsi":
            encyFile()
        else:
            decyFile()

    # ============= TAB 3: TEXT =============
    with tab4:
        st.header("Enkripsi Catatan & Diagnosis Medis")
        col_default, _ = st.columns([8, 1])
    with col_default:
        if st.button("Isi Key Default"):
            st.session_state.caesar_key = 3
            st.session_state.vigenere_key = "MEDIS"
            st.session_state.rc4_key = "RAHASIA"
            st.session_state.aes_key = "KUNCIENKRIPSI16"

        input_text = st.text_area("Masukkan Catatan Medis", height=100)
        
        # Caesar Key
        key = st.number_input("Masukkan Key Caesar", 
                            min_value=1, 
                            max_value=25, 
                            value=st.session_state.get('caesar_key', 3))
        
        # Kunci lainnya dengan default dari session state
        te.VIGENERE_KEY = st.text_input("Masukkan Key Vigenere", 
                                        type="password", 
                                        value=st.session_state.get('vigenere_key', ''))
        te.RC4_KEY = st.text_input("Masukkan Key RC4", 
                                type="password", 
                                value=st.session_state.get('rc4_key', ''))
        te.AES_KEY = st.text_input("Masukkan Key AES", 
                                type="password", 
                                value=st.session_state.get('aes_key', ''))
        if len(te.AES_KEY) != 16 or len(te.AES_KEY) != 32 or len(te.AES_KEY) != 64 :
            st.error("kunci AES harus memiliki panjang 16, 32, atau 64")
            
        col1, col2 = st.columns(2)
        
        try:
            with col1:
                if st.button("🔒 Enkripsi"):
                    if input_text:
                        result = te.super_encrypt(input_text, key)
                        st.text_area("Hasil Enkripsi", result, height=100)
                        if result:
                            conn = sqlite3.connect('users.db')
                            c = conn.cursor()
                            if 'id' in st.session_state:
                                c.execute("INSERT INTO text (user_id, enkripsi, key) VALUES (?, ?, ?)", (st.session_state.id, result, str(key)+"|"+te.VIGENERE_KEY+"|"+te.RC4_KEY+"|"+te.AES_KEY))
                            else:
                                st.error("User ID not found in session state.")
                            conn.commit()
                            conn.close()
                            st.success("Data berhasil disimpan.")

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
    
    with tab5:
        st.header("Riwayat Enkripsi Data Medis")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS text
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         enkripsi TEXT NOT NULL,
         key TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         user_id INTEGER NOT NULL,
         FOREIGN KEY(user_id) REFERENCES users(id))
    ''')
        data = pd.read_sql_query("SELECT * FROM text WHERE user_id = ?", conn, params=(st.session_state.id,))
        if not data.empty:
            st.dataframe(data)
        else:
            st.info("Belum ada data yang disimpan.")

def main():
    st.set_page_config(
        page_title="Sistem Keamanan Data Medis",
        page_icon="🏥",
        layout="wide"
    )

    
    st.markdown("""
        <style>
        /* Import custom theme CSS */
        @import url('medical-theme-css.css');
        
        /* Additional custom styles */
        .main {
            background-color: #B8CBEA;
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #3B365F !important;
            color: white !important;
        }
        .stForm {
            background-color: #474955;
            padding: 20px;
            border-radius: 10px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .viewerBadge_container__1QSob {display: none;}
        
        /* Custom header styles */
        h1 {
            color: #3B365F !important;
            font-weight: bold !important;
            padding: 1rem 0;
        }
        
        </style>
    """, unsafe_allow_html=True)
    
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Tampilkan login form atau aplikasi utama
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🏥 Login Sistem Keamanan Data Medis")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    verify_credentials = conn.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{hash_password(password)}'").fetchone()
                    if verify_credentials:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.id = verify_credentials[0]
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