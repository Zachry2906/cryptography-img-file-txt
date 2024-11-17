
# Aplikasi Enkripsi dengan Streamlit

## Deskripsi
Aplikasi ini adalah antarmuka web yang dibangun menggunakan Streamlit untuk mengenkripsi dan mendekripsi berbagai jenis data, termasuk gambar, file, dan teks. Aplikasi ini mendukung metode enkripsi yang beragam, seperti Caesar Cipher, Vigenere Cipher, RC4, AES-ECB, serta teknik steganografi untuk menyembunyikan pesan dalam gambar.

## Fitur
1. **Login dan Otentikasi**:
   - Pengguna harus login dengan nama pengguna dan kata sandi yang terenkripsi menggunakan SHA-256 untuk mengakses aplikasi.

2. **Enkripsi Gambar**:
   - Menggunakan metode XOR untuk enkripsi gambar.
   - Deteksi otomatis apakah gambar sudah terenkripsi atau belum.

3. **Steganografi Gambar**:
   - Menyembunyikan pesan teks dalam gambar dengan kunci enkripsi.
   - Pesan yang tersembunyi dapat didekripsi kembali menggunakan kunci yang benar.

4. **Enkripsi File**:
   - Enkripsi dan dekripsi file menggunakan teknik Fernet.

5. **Enkripsi Teks Super**:
   - Kombinasi dari beberapa metode enkripsi (Caesar, Vigenere, RC4, dan AES-ECB) untuk enkripsi teks yang kuat.

6. **Penyimpanan Data Enkripsi**:
   - Data enkripsi pengguna disimpan dalam database SQLite untuk pengelolaan yang aman dan terstruktur.

## Instalasi
1. **Kloning Repositori**:
   ```bash
   git clone https://github.com/username/repo-name.git
   cd repo-name
   ```

2. **Instalasi Dependencies**:
   Pastikan `Python 3.7+` terpasang. Lalu instal dependencies dengan:
   ```bash
   pip install -r requirements.txt
   ```

3. **Inisialisasi Database**:
   Buat database SQLite baru dengan nama `users.db` dan struktur tabel yang dibutuhkan seperti pada aplikasi.

## Penggunaan
1. **Jalankan Aplikasi Streamlit**:
   ```bash
   streamlit run app.py
   ```

2. **Fitur Login**:
   - Login atau buat akun baru (melalui akses database secara langsung untuk penambahan user).
   
3. **Navigasi Aplikasi**:
   - Setelah login, aplikasi menyediakan berbagai tab untuk fitur enkripsi dan dekripsi yang tersedia.

## Struktur Kode
- `app.py`: Mengelola antarmuka pengguna dan logika utama aplikasi.
- `process/`: Berisi modul pemrosesan enkripsi, dekripsi, dan steganografi:
  - `utliss.py`: Fungsi utilitas untuk mendeteksi status enkripsi file.
  - `imageProc.py`: Fungsi untuk enkripsi dan dekripsi gambar.
  - `fileProc.py`: Fungsi untuk enkripsi dan dekripsi file.
  - `textProc.py`: Fungsi untuk berbagai metode enkripsi teks.

## Contoh Metode Enkripsi
1. **Caesar Cipher**: Menggeser huruf dengan kunci angka.
2. **Vigenere Cipher**: Menggunakan kata kunci untuk menggeser huruf pada teks.
3. **RC4**: Stream cipher berbasis kunci string.
4. **AES-ECB**: Metode block cipher dengan kunci tetap.

## Lisensi
Proyek ini dilisensikan di bawah lisensi MIT.
