import sqlite3
import os
import streamlit_authenticator as stauth

# Ensure the database folder exists
os.makedirs('database', exist_ok=True)

# 1. Connect to SQLite (This creates the file if it doesn't exist)
conn = sqlite3.connect('database/users.db')
cursor = conn.cursor()

# 2. Create the Users Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

# 3. Create the Tracked Software Table
# This uses a Foreign Key to link the software to a specific user
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracked_software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        software_name TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username),
        UNIQUE(username, software_name) -- Prevents tracking the same thing twice
    )
''')

# 4. Create your default Admin account
admin_username = "admin"
admin_name = "Austin Espinoza"
admin_email = "austin@example.com"
plain_text_password = "password123" # Change this!

# Securely hash the password using bcrypt
hashed_password = stauth.Hasher.hash(plain_text_password)

try:
    cursor.execute('''
        INSERT INTO users (username, name, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (admin_username, admin_name, admin_email, hashed_password))
    print(f"✅ Successfully created user: {admin_username}")
except sqlite3.IntegrityError:
    print(f"⚠️ User '{admin_username}' already exists in the database.")

# 5. Add some default tracked software just to test
try:
    cursor.execute("INSERT INTO tracked_software (username, software_name) VALUES (?, ?)", ("admin", "Windows 10"))
    cursor.execute("INSERT INTO tracked_software (username, software_name) VALUES (?, ?)", ("admin", "Apache"))
except sqlite3.IntegrityError:
    pass

conn.commit()
conn.close()
print("💾 Database initialization complete!")