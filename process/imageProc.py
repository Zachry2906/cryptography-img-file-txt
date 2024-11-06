import streamlit as st
from io import BytesIO
from PIL import Image
from process.utliss import encrypt_image_xor
import numpy as np

def encyImage(key, is_enc, file_data,upload_image) :
    if st.button("🔓 Enkripsi Gambar"):
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


def decyImage(key, file_data,upload_image) :
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
                    # img.save menyimpan gambar ke dalam BytesIO
                    # format=img.format untuk menyimpan format gambar yang sama dengan format asli
                    img_byte_arr = img_byte_arr.getvalue()
                    # img_btte_arr berisi data gambar yang sudah di dekripsi bertipe data bytes
                    
                    # Tampilkan gambar hasil dekripsi
                    st.image(img_byte_arr, caption="Hasil Dekripsi", use_column_width=True)
                    # st.image mereima parameter data gambar yang akan ditampilkan
                    
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


def encyStegano(text, key, is_enc, file_data, upload_image):
    # Periksa apakah key kosong
    if not key:
        st.error("Key harus diisi sebelum menyisipkan pesan.")
        return

    # Konversi gambar menjadi array numpy
    image = Image.open(upload_image)
    image_np = np.array(image)

    # Convert message to binary
    binary_text = ''.join(format(ord(char), '08b') for char in text)
    binary_key = format(int(key), '08b')  # Kunci dalam format biner

    # Loop untuk menyisipkan pesan ke dalam bit terakhir dari setiap piksel
    data_index = 0
    for i in range(image_np.shape[0]):
        for j in range(image_np.shape[1]):
            pixel = image_np[i, j]
            for k in range(3):  # Untuk setiap kanal RGB
                if data_index < len(binary_text):
                    pixel[k] = int(bin(pixel[k])[:-1] + binary_text[data_index], 2)
                    data_index += 1
                else:
                    break
        if data_index >= len(binary_text):
            break

    # Simpan gambar hasil steganografi
    stego_image = Image.fromarray(image_np)
    stego_image.save("stego_image.png")
    st.image("stego_image.png", caption="Gambar dengan Pesan Tersimpan", use_column_width=True)
    st.download_button(
        label="💾 Unduh Gambar dengan Pesan",
        data=open("stego_image.png", "rb"),
        file_name="stego_image.png",
        mime="image/png"
    )
    st.success("Pesan berhasil disisipkan ke dalam gambar.")

# Fungsi untuk mendekripsi pesan dari gambar
def decyStegano(key, file_data, upload_image):
    if not key:
        st.error("Key harus diisi sebelum mengekstraksi pesan.")
        return

    # Konversi gambar menjadi array numpy
    image = Image.open(upload_image)
    image_np = np.array(image)

    # Ekstraksi pesan dari bit terakhir setiap piksel
    binary_text = ''
    for i in range(image_np.shape[0]):
        for j in range(image_np.shape[1]):
            pixel = image_np[i, j]
            for k in range(3):  # Untuk setiap kanal RGB
                binary_text += bin(pixel[k])[-1]  # Dapatkan bit terakhir

    # Konversi dari biner ke teks
    decoded_text = ''.join(chr(int(binary_text[i:i+8], 2)) for i in range(0, len(binary_text), 8))

    # Tampilkan hasil ekstraksi
    st.text_area("Pesan yang Diekstrak", value=decoded_text, height=100)
    st.success("Pesan berhasil diekstraksi.")
 