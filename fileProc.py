import streamlit as st
from utliss import generate_key, encrypt_file, decrypt_file, create_zip_with_key_and_file

def encyFile() :
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

def decyFile() :
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