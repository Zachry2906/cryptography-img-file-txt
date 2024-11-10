import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()