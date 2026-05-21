import sqlite3
import hashlib
import os
import re

# ─── DATABASE SETUP ───────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ─── PASSWORD HASHING ─────────────────────────────────────────────────────────

def generate_salt():
    return os.urandom(16).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

# ─── VALIDATION ───────────────────────────────────────────────────────────────

def is_valid_email(email):
    return re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email)

def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain an uppercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain a number."
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Password must contain a special character (!@#$%^&*)."
    return True, "Strong"

# ─── SIGNUP ───────────────────────────────────────────────────────────────────

def signup():
    print("\n📝 SIGNUP")
    print("-" * 30)

    username = input("Enter username: ").strip()
    if not username:
        print("❌ Username cannot be empty.")
        return

    email = input("Enter email: ").strip()
    if not is_valid_email(email):
        print("❌ Invalid email format.")
        return

    password = input("Enter password: ").strip()
    valid, msg = is_strong_password(password)
    if not valid:
        print(f"❌ {msg}")
        return

    confirm = input("Confirm password: ").strip()
    if password != confirm:
        print("❌ Passwords do not match.")
        return

    salt = generate_salt()
    password_hash = hash_password(password, salt)

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, salt)
        )
        conn.commit()
        conn.close()
        print(f"\n✅ Account created successfully! Welcome, {username}!")
    except sqlite3.IntegrityError:
        print("❌ Username or email already exists.")

# ─── LOGIN ────────────────────────────────────────────────────────────────────

def login():
    print("\n🔐 LOGIN")
    print("-" * 30)

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        print("❌ User not found.")
        return

    stored_hash, salt = result
    entered_hash = hash_password(password, salt)

    if entered_hash == stored_hash:
        print(f"\n✅ Login successful! Welcome back, {username}!")
    else:
        print("❌ Incorrect password.")

# ─── VIEW USERS (Admin/Demo) ──────────────────────────────────────────────────

def view_users():
    print("\n👥 REGISTERED USERS")
    print("-" * 40)
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()
    conn.close()

    if not users:
        print("No users registered yet.")
    else:
        print(f"{'ID':<5} {'Username':<20} {'Email'}")
        print("-" * 40)
        for u in users:
            print(f"{u[0]:<5} {u[1]:<20} {u[2]}")

# ─── MAIN MENU ────────────────────────────────────────────────────────────────

def main():
    init_db()
    print("\n" + "="*40)
    print("   🔒 Secure Login Authentication System")
    print("="*40)

    while True:
        print("\n1. Signup")
        print("2. Login")
        print("3. View Users (Demo)")
        print("4. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            signup()
        elif choice == "2":
            login()
        elif choice == "3":
            view_users()
        elif choice == "4":
            print("\nGoodbye! 👋")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()