import streamlit as st
from cryptography.fernet import Fernet
import base64
import os
from pathlib import Path
import numpy as np
from io import BytesIO
from PIL import Image
import zipfile

# ============= FUNGSI UTILITAS =============
def generate_key():
    """Menghasilkan kunci enkripsi baru untuk Fernet"""
    return Fernet.generate_key()

def encrypt_file(file_bytes, key):
    """Mengenkripsi file menggunakan Fernet"""
    f = Fernet(key)
    encrypted_data = f.encrypt(file_bytes)
    return encrypted_data

def decrypt_file(encrypted_bytes, key):
    """Mendekripsi file menggunakan Fernet"""
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_bytes)
    return decrypted_data

def create_zip_with_key_and_file(encrypted_data, key, original_filename):
    """Membuat file ZIP yang berisi file terenkripsi dan key"""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Menambahkan file terenkripsi
        zip_file.writestr(f"encrypted_{original_filename}", encrypted_data)
        # Menambahkan file key
        zip_file.writestr("encryption_key.key", key)
    return zip_buffer.getvalue()

def encrypt_image_xor(image_data, key):
    """Mengenkripsi gambar menggunakan XOR"""
    try:
        key_byte = int(key) % 256
        img = bytearray(image_data)
        for index, value in enumerate(img):
            img[index] = value ^ key_byte
        return BytesIO(img)
    except ValueError as e:
        st.error("Key harus berupa angka untuk enkripsi XOR.")
        return None

def is_encrypted(file_data):
    """Memeriksa apakah file adalah gambar terenkripsi"""
    try:
        Image.open(BytesIO(file_data))
        return False
    except:
        return True

# ============= KONFIGURASI APLIKASI =============
st.set_page_config(page_title="Enkripsi App", page_icon="🔒")
st.title("🔒 Aplikasi Enkripsi")
st.markdown("Enkripsi file dan gambar Anda dengan aman menggunakan berbagai metode enkripsi")

# ============= TAB SYSTEM =============
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
            if st.button("🔒 Enkripsi Gambar"):
                if key and not is_enc:
                    # Proses enkripsi
                    encrypted_img = encrypt_image_xor(file_data, key)
                    
                    if encrypted_img:
                        st.download_button(
                            label="💾 Unduh Gambar Terenkripsi",
                            data=encrypted_img.getvalue(),
                            file_name=f"encrypted_{upload_image.name}",
                            mime="image/png"
                        )
                        st.success("✅ Enkripsi berhasil!")
                        st.warning("⚠️ Simpan key dengan aman untuk dekripsi!")
                else:
                    if is_enc:
                        st.error("File sudah terenkripsi!")
                    else:
                        st.error("❌ Masukkan key terlebih dahulu!")

        with col2:
            if st.button("🔓 Dekripsi Gambar"):
                if key:
                    # Proses dekripsi
                    decrypted_img = encrypt_image_xor(file_data, key)
                    
                    if decrypted_img:
                        try:
                            # Coba buka hasil dekripsi sebagai gambar
                            img = Image.open(decrypted_img)
                            # Konversi kembali ke BytesIO untuk ditampilkan
                            img_byte_arr = BytesIO()
                            img.save(img_byte_arr, format=img.format if img.format else 'PNG')
                            img_byte_arr = img_byte_arr.getvalue()
                            
                            # Tampilkan gambar hasil dekripsi
                            st.image(img_byte_arr, caption="Hasil Dekripsi", use_column_width=True)
                            
                            # Tombol download
                            st.download_button(
                                label="💾 Unduh Gambar Terdekripsi",
                                data=img_byte_arr,
                                file_name=f"decrypted_{upload_image.name}",
                                mime="image/png"
                            )
                            st.success("✅ Dekripsi berhasil!")
                        except Exception as e:
                            st.error("❌ Dekripsi gagal. Pastikan key yang digunakan benar!")
                            st.error(f"Detail error: {str(e)}")
                else:
                    st.error("❌ Masukkan key terlebih dahulu!")

# ============= TAB 2: ENKRIPSI FILE =============
with tab2:
    st.header("Enkripsi File dengan Fernet")
    
    # Mode selection
    mode = st.radio("Pilih Mode:", ("🔒 Enkripsi", "🔓 Dekripsi"))
    
    if mode == "🔒 Enkripsi":
        uploaded_file = st.file_uploader("Pilih file untuk dienkripsi", type=None, key="enc_file")
        
        if uploaded_file is not None:
            if st.button("🔒 Enkripsi dan Download"):
                try:
                    # Generate kunci
                    key = generate_key()
                    # Enkripsi file
                    file_bytes = uploaded_file.getvalue()
                    encrypted_data = encrypt_file(file_bytes, key)
                    
                    # Buat ZIP dengan file terenkripsi dan key
                    zip_data = create_zip_with_key_and_file(
                        encrypted_data,
                        key,
                        uploaded_file.name
                    )
                    
                    # Download ZIP
                    st.download_button(
                        label="📦 Download File Enkripsi & Key",
                        data=zip_data,
                        file_name=f"encrypted_{uploaded_file.name}.zip",
                        mime="application/zip"
                    )
                    
                    st.success("✅ File berhasil dienkripsi!")
                    st.warning("⚠️ PENTING: File ZIP berisi file terenkripsi dan key. Simpan dengan aman!")
                
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")
    
    else:  # Mode Dekripsi
        col1, col2 = st.columns(2)
        with col1:
            encrypted_file = st.file_uploader("Pilih file terenkripsi", type=None, key="dec_file")
        with col2:
            key_file = st.file_uploader("Upload kunci enkripsi", type=["key"])
        
        if encrypted_file is not None and key_file is not None:
            if st.button("🔓 Dekripsi File"):
                try:
                    key = key_file.read()
                    encrypted_data = encrypted_file.getvalue()
                    decrypted_data = decrypt_file(encrypted_data, key)
                    
                    file_name = encrypted_file.name
                    if file_name.startswith("encrypted_"):
                        file_name = file_name[10:]
                    
                    st.download_button(
                        label="💾 Download File Terdekripsi",
                        data=decrypted_data,
                        file_name=f"decrypted_{file_name}",
                        mime="application/octet-stream"
                    )
                    
                    st.success("✅ File berhasil didekripsi!")
                    
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")
                    st.error("Pastikan file dan kunci yang digunakan benar!")

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