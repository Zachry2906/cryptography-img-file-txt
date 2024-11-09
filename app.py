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

# Function to encode the message into the image
def encode_message(message, image):
    encoded_image = image.copy()

    # Encoding the message into the image
    encoded_image.putdata(encode_data(image, message))

    # Save the encoded image
    encoded_image_path = "encoded.png"
    encoded_image.save(encoded_image_path)

    st.success("Image encoded successfully.")
    show_encoded_image(encoded_image_path)


# Function to decode the hidden message from the image
def decode_message(image, key):
    # Decode the hidden message from the image
    decoded_message = decode_data(image)
    decripted_message = te.caesar_decrypt(decoded_message, key)
    # show_decoded_image(image)  # Call the function to display the decoded image
    return decripted_message


# Function to display the decoded image in the UI
# def show_decoded_image(decoded_image):
#     st.image(decoded_image, caption="Decoded Image", use_column_width=True)


# Function to encode the data (message) into the image
def encode_data(image, data):
    data = data + "$"  # Adding a delimiter to identify the end of the message
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


# Function to decode the data (message) from the image
def decode_data(image):
    pixels = list(image.getdata())

    data_bin = ""
    for pixel in pixels:
        # Extracting the least significant bit of the red channel
        data_bin += bin(pixel[0])[-1]

    data = ""
    for i in range(0, len(data_bin), 8):
        byte = data_bin[i:i + 8]
        data += chr(int(byte, 2))
        if data[-1] == "$":
            break

    return data[:-1]  # Removing the delimiter


# Function to display the encoded image in the UI and add a download button
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
    st.title("🔒 Aplikasi Enkripsi")
    st.markdown("Enkripsi file dan gambar Anda dengan aman menggunakan berbagai metode enkripsi")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📸 Enkripsi Gambar", "📸 Steganografi Gambar", "📁 Enkripsi File", "📝 Enkripsi Text", "📈 Data Anda"])

    # ============= TAB 1: ENKRIPSI GAMBAR =============
    with tab1:
        st.header("Enkripsi Gambar dengan XOR (ini salah jir, ga disuruh)")
        upload_image = st.file_uploader("Unggah gambar", type=["jpg", "png", "jpeg", "bmp"], key='image')

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
            st.header("Encode")
            pesan = st.text_input("Masukkan Pesan Rahasia")
            key = st.text_input("Masukkan Kunci", type="password", key='encode')
            message = te.caesar_encrypt(pesan, key)
            # password = col1.text_input("Enter Password", type="password")
            image_file = st.file_uploader("Pilih Gambar", type=["png", "jpg", "jpeg"])
        with col2:
            st.header("Encoded Image")
            if message and image_file:
                image = Image.open(image_file)
                encode_message(message, image)

        st.markdown("---")

        col3, col4 = st.columns(2)
        with col3:
            st.header("Decode")
            keyDecy = st.text_input("Masukkan Kunci", type="password", key='decode')
        with col4:
            st.header("Pesan Rahasia")

        # decode_password = col3.text_input("Enter Password for Decoding", type="password")
        decode_image_file = col3.file_uploader(
            "Pilih Gambar yang Ingin diketahui pesannya", type=["png", "jpg", "jpeg"]
        )

        if decode_image_file:
            decode_image = Image.open(decode_image_file)
            col4.write("Pesan Rahasia: " + decode_message(decode_image, keyDecy))

    # ============= TAB 3: ENKRIPSI FILE =============
    with tab3:
        st.header("Enkripsi File dengan Fernet")
        mode = st.radio("Pilih Mode:", ("🔒 Enkripsi", "🔓 Dekripsi"))
        
        if mode == "🔒 Enkripsi":
            encyFile()
        else:
            decyFile()

    # ============= TAB 3: TEXT =============
    with tab4:
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
        st.header("Data Anda")
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
    st.set_page_config(page_title="Tugas Akhir Kriptografi", page_icon="🔒")
    
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