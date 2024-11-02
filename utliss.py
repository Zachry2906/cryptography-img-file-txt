import streamlit as st
from cryptography.fernet import Fernet
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
        zip_file.writestr(f"encrypted_{original_filename}_key", key)
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