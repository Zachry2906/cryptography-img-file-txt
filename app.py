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

try:
    conn = sqlite3.connect('users.db')
except sqlite3.Error as e:
    st.error(f"Database connection error: {e}")

# Fungsi untuk mengenkripsi password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to encode the message into the image
def encode_message(message, image):
    try:
        encoded_image = image.copy()
        encoded_image.putdata(encode_data(image, message))
        encoded_image_path = "encoded.png"
        encoded_image.save(encoded_image_path)
        st.success("Image encoded successfully.")
        show_encoded_image(encoded_image_path)
    except Exception as e:
        st.error(f"Error encoding message: {e}")

# Function to decode the hidden message from the image
def decode_message(image, key):
    try:
        decoded_message = decode_data(image)
        decrypted_message = te.caesar_decrypt(decoded_message, key)
        return decrypted_message
    except Exception as e:
        st.error(f"Error decoding message: {e}")
        return ""

# Function to encode the data (message) into the image
def encode_data(image, data):
    try:
        data = data + "$"
        data_bin = ''.join(format(ord(char), '08b') for char in data)
        pixels = list(image.getdata())
        encoded_pixels = []
        index = 0
        for pixel in pixels:
            if index < len(data_bin):
                red_pixel = pixel[0]
                new_pixel = (red_pixel & 254) | int(data_bin[index])
                encoded_pixels.append((new_pixel, pixel[1], pixel[2]))
                index += 1
            else:
                encoded_pixels.append(pixel)
        return encoded_pixels
    except Exception as e:
        st.error(f"Error encoding data: {e}")
        return []

# Function to decode the data (message) from the image
def decode_data(image):
    try:
        pixels = list(image.getdata())
        data_bin = ""
        for pixel in pixels:
            data_bin += bin(pixel[0])[-1]
        data = ""
        for i in range(0, len(data_bin), 8):
            byte = data_bin[i:i + 8]
            data += chr(int(byte, 2))
            if data[-1] == "$":
                break
        return data[:-1]
    except Exception as e:
        st.error(f"Error decoding data: {e}")
        return ""

# Function to display the encoded image in the UI and add a download button
def show_encoded_image(image_path):
    try:
        encoded_image = Image.open(image_path)
        st.image(encoded_image, caption="Encoded Image", use_column_width=True)
        buffered = BytesIO()
        encoded_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        href = ('<a href="data:file/png;base64,' + img_str + '" '
                'download="' + image_path + '">Download Encoded Image</a>')
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying encoded image: {e}")

# Fungsi untuk menampilkan aplikasi utama
def main_app():
    st.title("🏥 Sistem Keamanan Data Medis")
    st.markdown("Enkripsi data medis pasien dengan aman menggunakan berbagai metode enkripsi")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📸 Enkripsi Citra Medis", 
        "📸 Steganografi Dokumen", 
        "📁 Enkripsi Berkas Pasien", 
        "📝 Enkripsi Catatan Medis",
        "📈 Riwayat Enkripsi"
    ])

    with tab1:
        st.header("Enkripsi Citra Medis dengan XOR")
        upload_image = st.file_uploader("Unggah hasil pemindaian medis (X-Ray, MRI, USG)", type=["jpg", "png", "jpeg", "bmp"])

        if upload_image is not None:
            try:
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
            except Exception as e:
                st.error(f"Error processing image: {e}")

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.header("Penyembunyian Data Pasien dalam Citra Medis")
            pesan = st.text_input("Masukkan Data Rahasia Pasien")
            key = st.text_input("Masukkan Kunci", type="password", key='encode')
            try:
                key = int(key)
            except ValueError:
                st.error("Key harus berupa angka.")
                return
            message = te.caesar_encrypt(pesan, key)
            image_file = st.file_uploader("Pilih Gambar", type=["png", "jpg", "jpeg"])
        with col2:
            st.header("Citra Medis dengan Data Rahasia")
            if message and image_file:
                try:
                    image = Image.open(image_file)
                    encode_message(message, image)
                except Exception as e:
                    st.error(f"Error encoding message into image: {e}")

        st.markdown("---")

        col3, col4 = st.columns(2)
        with col3:
            st.header("Ekstrak Data Rahasia dari Citra Medis")
            keyDecy = st.text_input("Masukkan Kunci", type="password", key='decode')
            try:
                keyDecy = int(keyDecy)
            except ValueError:
                st.error("Key harus berupa angka.")
                return
        with col4:
            st.header("Data Rahasia Pasien")
        decode_image_file = col3.file_uploader("Pilih Gambar yang Ingin diketahui pesannya", type=["png", "jpg", "jpeg"])

        if decode_image_file:
            try:
                decode_image = Image.open(decode_image_file)
                col4.write("Pesan Rahasia: " + decode_message(decode_image, keyDecy))
            except Exception as e:
                st.error(f"Error decoding message from image: {e}")

    with tab3:
        st.header("Enkripsi Berkas Rekam Medis dengan Fernet")
        mode = st.radio("Pilih Mode:", ("🔒 Enkripsi", "🔓 Dekripsi"))
        try:
            if mode == "🔒 Enkripsi":
                encyFile()
            else:
                decyFile()
        except Exception as e:
            st.error(f"Error processing file: {e}")

    with tab4:
        st.header("Enkripsi Catatan & Diagnosis Medis")
        input_text = st.text_area("Masukkan Catatan Medis", height=100)
        key = st.number_input("Masukkan Key caesar", min_value=1, max_value=25, value=3)
        te.VIGENERE_KEY = st.text_input("Masukkan Key Vigenere", type="password")
        te.RC4_KEY = st.text_input("Masukkan Key RC4", type="password")
        te.AES_KEY = st.text_input("Masukkan Key AES", type="password")
        if len(te.AES_KEY) not in [16, 32, 64]:
            st.error("kunci AES harus memiliki panjang 16, 32, atau 64")
        col1, col2 = st.columns(2)
        try:
            with col1:
                if st.button("🔒 Enkripsi"):
                    if input_text:
                        result = te.super_encrypt(input_text, key)
                        st.text_area("Hasil Enkripsi", result, height=100)
                        if result:
                            try:
                                conn = sqlite3.connect('users.db')
                                c = conn.cursor()
                                if 'id' in st.session_state:
                                    c.execute("INSERT INTO text (user_id, enkripsi, key) VALUES (?, ?, ?)", (st.session_state.id, result, str(key)+"|"+te.VIGENERE_KEY+"|"+te.RC4_KEY+"|"+te.AES_KEY))
                                else:
                                    st.error("User ID not found in session state.")
                                conn.commit()
                                conn.close()
                                st.success("Data berhasil disimpan.")
                            except sqlite3.Error as e:
                                st.error(f"Database error: {e}")
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
        try:
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
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")

def main():
    st.set_page_config(
        page_title="Sistem Keamanan Data Medis",
        page_icon="🏥",
        layout="wide"
    )

    st.markdown("""
        <style>
        @import url('medical-theme-css.css');
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
        h1 {
            color: #3B365F !important;
            font-weight: bold !important;
            padding: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🏥 Login Sistem Keamanan Data Medis")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                if submit:
                    try:
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
                    except sqlite3.Error as e:
                        st.error(f"Database error: {e}")
    else:
        with st.sidebar:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.rerun()
        main_app()

if __name__ == "__main__":
    main()
