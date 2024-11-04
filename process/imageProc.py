import streamlit as st
from io import BytesIO
from PIL import Image
from process.utliss import encrypt_image_xor

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