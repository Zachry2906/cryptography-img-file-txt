import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

# Fungsi untuk inisialisasi database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         password TEXT NOT NULL,
         role TEXT NOT NULL,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    
    # Cek apakah admin default sudah ada
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        # Tambahkan admin default
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 ('admin', admin_password, 'admin'))
    
    conn.commit()
    conn.close()

# Fungsi untuk hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi untuk verifikasi login
def verify_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password, role FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0] == hash_password(password):
        return True, result[1]
    return False, None

# Fungsi untuk menambah user baru
def add_user(username, password, role):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        hashed_password = hash_password(password)
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, hashed_password, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Fungsi untuk mendapatkan semua user
def get_all_users():
    conn = sqlite3.connect('users.db')
    users = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return users

# Fungsi untuk menghapus user
def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=? AND username!='admin'", (user_id,))
    conn.commit()
    conn.close()

# Fungsi untuk mengubah password
def change_password(username, new_password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = hash_password(new_password)
    c.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
    conn.commit()
    conn.close()

# Panel Admin
def admin_panel():
    st.title("👥 Panel Admin")
    
    # Tab untuk manajemen user
    tab1, tab2 = st.tabs(["📊 Daftar User", "➕ Tambah User"])
    
    with tab1:
        st.subheader("Daftar User")
        users_df = get_all_users()
        st.dataframe(users_df)
        
        # Hapus user
        if len(users_df) > 0:
            user_to_delete = st.selectbox("Pilih user untuk dihapus:",
                                        users_df[users_df['username'] != 'admin']['username'])
            if st.button("🗑️ Hapus User"):
                user_id = users_df[users_df['username'] == user_to_delete]['id'].iloc[0]
                delete_user(user_id)
                st.success(f"User {user_to_delete} berhasil dihapus!")
                st.rerun()
    
    with tab2:
        st.subheader("Tambah User Baru")
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            
            if st.form_submit_button("➕ Tambah User"):
                if new_username and new_password:
                    if add_user(new_username, new_password, new_role):
                        st.success(f"User {new_username} berhasil ditambahkan!")
                        st.rerun()
                    else:
                        st.error("Username sudah digunakan!")
                else:
                    st.error("Username dan password harus diisi!")

# Fungsi untuk mengubah password user
def change_password_form():
    st.subheader("🔑 Ubah Password")
    with st.form("change_password_form"):
        current_password = st.text_input("Password Saat Ini", type="password")
        new_password = st.text_input("Password Baru", type="password")
        confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
        
        if st.form_submit_button("Ubah Password"):
            if verify_login(st.session_state.username, current_password)[0]:
                if new_password == confirm_password:
                    change_password(st.session_state.username, new_password)
                    st.success("Password berhasil diubah!")
                    st.session_state.logged_in = False
                    st.rerun()
                else:
                    st.error("Password baru tidak cocok!")
            else:
                st.error("Password saat ini salah!")

def main():
    # Inisialisasi database
    init_db()
    
    # Konfigurasi halaman
    st.set_page_config(page_title="Login System", page_icon="🔒", layout="wide")
    
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # CSS kustom
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
        </style>
    """, unsafe_allow_html=True)
    
    # Proses login/logout
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🔒 Login System")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    login_successful, role = verify_login(username, password)
                    if login_successful:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.success("Login berhasil!")
                        st.rerun()
                    else:
                        st.error("Username atau password salah!")
    else:
        # Sidebar
        with st.sidebar:
            st.write(f"👤 **{st.session_state.username}**")
            st.write(f"🎭 Role: {st.session_state.role}")
            
            if st.button("📱 Menu Utama"):
                st.session_state.current_page = 'main'
            
            if st.button("🔑 Ubah Password"):
                st.session_state.current_page = 'change_password'
            
            if st.session_state.role == 'admin':
                if st.button("👥 Panel Admin"):
                    st.session_state.current_page = 'admin'
            
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.rerun()
        
        # Tampilkan halaman yang sesuai
        if not hasattr(st.session_state, 'current_page'):
            st.session_state.current_page = 'main'
        
        if st.session_state.current_page == 'main':
            st.title("🏠 Halaman Utama")
            st.write(f"Selamat datang, {st.session_state.username}!")
        elif st.session_state.current_page == 'admin' and st.session_state.role == 'admin':
            admin_panel()
        elif st.session_state.current_page == 'change_password':
            change_password_form()

if __name__ == "__main__":
    main()