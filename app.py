from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import hashlib
import os
import re

app = Flask(__name__)
app.secret_key = "cybersec_secret_key_2024"

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

def generate_salt():
    return os.urandom(16).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def is_strong_password(password):
    if len(password) < 8:
        return False, "At least 8 characters required"
    if not re.search(r'[A-Z]', password):
        return False, "Add an uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Add a number"
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Add a special character (!@#$%^&*)"
    return True, "Strong"

BASE_STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: #0a0a0f;
    color: #e0e0e0;
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
      repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(0,255,136,0.03) 40px, rgba(0,255,136,0.03) 41px),
      repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(0,255,136,0.03) 40px, rgba(0,255,136,0.03) 41px);
    pointer-events: none;
    z-index: 0;
  }

  .card {
    background: rgba(10, 20, 15, 0.95);
    border: 1px solid rgba(0,255,136,0.25);
    border-radius: 4px;
    padding: 40px;
    width: 420px;
    position: relative;
    z-index: 1;
    box-shadow: 0 0 40px rgba(0,255,136,0.08), inset 0 0 40px rgba(0,0,0,0.5);
    animation: fadeIn 0.4s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .card::before {
    content: '';
    position: absolute;
    top: -1px; left: 20px; right: 20px; height: 2px;
    background: linear-gradient(90deg, transparent, #00ff88, transparent);
  }

  .logo {
    text-align: center;
    margin-bottom: 32px;
  }

  .logo h1 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 22px;
    color: #00ff88;
    letter-spacing: 3px;
    text-transform: uppercase;
  }

  .logo p {
    font-size: 12px;
    color: #444;
    letter-spacing: 2px;
    margin-top: 6px;
    font-family: 'Share Tech Mono', monospace;
  }

  .form-group {
    margin-bottom: 18px;
  }

  label {
    display: block;
    font-size: 11px;
    letter-spacing: 2px;
    color: #00ff88;
    margin-bottom: 6px;
    text-transform: uppercase;
    font-family: 'Share Tech Mono', monospace;
  }

  input {
    width: 100%;
    background: rgba(0,255,136,0.04);
    border: 1px solid rgba(0,255,136,0.2);
    border-radius: 2px;
    padding: 12px 14px;
    color: #e0e0e0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  input:focus {
    border-color: #00ff88;
    box-shadow: 0 0 12px rgba(0,255,136,0.15);
  }

  input::placeholder { color: #333; }

  .btn {
    width: 100%;
    padding: 14px;
    background: transparent;
    border: 1px solid #00ff88;
    color: #00ff88;
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    letter-spacing: 3px;
    text-transform: uppercase;
    cursor: pointer;
    border-radius: 2px;
    margin-top: 8px;
    transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  }

  .btn:hover {
    background: #00ff88;
    color: #0a0a0f;
    box-shadow: 0 0 20px rgba(0,255,136,0.3);
  }

  .btn-secondary {
    border-color: #333;
    color: #555;
    margin-top: 10px;
  }

  .btn-secondary:hover {
    background: #1a1a1a;
    color: #888;
    box-shadow: none;
  }

  .alert {
    padding: 10px 14px;
    border-radius: 2px;
    margin-bottom: 18px;
    font-size: 13px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 1px;
  }

  .alert-error {
    background: rgba(255,50,50,0.08);
    border: 1px solid rgba(255,50,50,0.3);
    color: #ff5555;
  }

  .alert-success {
    background: rgba(0,255,136,0.08);
    border: 1px solid rgba(0,255,136,0.3);
    color: #00ff88;
  }

  .link {
    text-align: center;
    margin-top: 20px;
    font-size: 13px;
    color: #444;
    font-family: 'Share Tech Mono', monospace;
  }

  .link a {
    color: #00ff88;
    text-decoration: none;
  }

  .link a:hover { text-decoration: underline; }

  .divider {
    border: none;
    border-top: 1px solid rgba(0,255,136,0.1);
    margin: 24px 0;
  }

  .dashboard { width: 520px; }

  .dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
  }

  .dash-title {
    font-family: 'Share Tech Mono', monospace;
    color: #00ff88;
    font-size: 16px;
    letter-spacing: 2px;
  }

  .badge {
    background: rgba(0,255,136,0.1);
    border: 1px solid rgba(0,255,136,0.3);
    color: #00ff88;
    padding: 4px 12px;
    border-radius: 2px;
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 2px;
  }

  .info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 24px;
  }

  .info-box {
    background: rgba(0,255,136,0.04);
    border: 1px solid rgba(0,255,136,0.12);
    border-radius: 2px;
    padding: 16px;
  }

  .info-box .label {
    font-size: 10px;
    color: #444;
    letter-spacing: 2px;
    font-family: 'Share Tech Mono', monospace;
    text-transform: uppercase;
    margin-bottom: 6px;
  }

  .info-box .value {
    font-size: 15px;
    color: #e0e0e0;
    font-family: 'Share Tech Mono', monospace;
  }

  .status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #00ff88;
    border-radius: 50%;
    margin-right: 6px;
    box-shadow: 0 0 8px #00ff88;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }
</style>
"""

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, email, password_hash, salt FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            error = "User not found."
        else:
            stored_hash = result[2]
            salt = result[3]
            if hash_password(password, salt) == stored_hash:
                session['user'] = result[0]
                session['email'] = result[1]
                return redirect(url_for('dashboard'))
            else:
                error = "Incorrect password."

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head><title>SecureAuth | Login</title>{BASE_STYLE}</head>
    <body>
      <div class="card">
        <div class="logo">
          <h1>SecureAuth</h1>
          <p>AUTHENTICATION SYSTEM</p>
        </div>
        {'<div class="alert alert-error">' + error + '</div>' if error else ''}
        <div class="form-group">
          <label>Username</label>
          <input type="text" name="username" placeholder="Enter username" form="loginForm" required>
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" name="password" placeholder="Enter password" form="loginForm" required>
        </div>
        <form id="loginForm" method="POST" action="/login">
          <input type="hidden" name="username" id="u">
          <input type="hidden" name="password" id="p">
        </form>
        <button class="btn" onclick="submitLogin()">Login</button>
        <hr class="divider">
        <div class="link">No account? <a href="/signup">Create one</a></div>
      </div>
      <script>
        const inputs = document.querySelectorAll('input[type=text], input[type=password]');
        function submitLogin() {{
          document.getElementById('u').value = inputs[0].value;
          document.getElementById('p').value = inputs[1].value;
          document.getElementById('loginForm').submit();
        }}
      </script>
    </body>
    </html>
    """)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    success = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        confirm = request.form['confirm'].strip()

        if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
            error = "Invalid email format."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            valid, msg = is_strong_password(password)
            if not valid:
                error = msg
            else:
                salt = generate_salt()
                pw_hash = hash_password(password, salt)
                try:
                    conn = sqlite3.connect("users.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                        (username, email, pw_hash, salt)
                    )
                    conn.commit()
                    conn.close()
                    success = f"Account created! Welcome, {username}."
                except sqlite3.IntegrityError:
                    error = "Username or email already exists."

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head><title>SecureAuth | Signup</title>{BASE_STYLE}</head>
    <body>
      <div class="card">
        <div class="logo">
          <h1>SecureAuth</h1>
          <p>CREATE ACCOUNT</p>
        </div>
        {'<div class="alert alert-error">' + error + '</div>' if error else ''}
        {'<div class="alert alert-success">' + success + ' <a href="/login" style="color:#00ff88">Login</a></div>' if success else ''}
        <form method="POST" action="/signup">
          <div class="form-group">
            <label>Username</label>
            <input type="text" name="username" placeholder="Choose a username" required>
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" placeholder="your@email.com" required>
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" placeholder="Min 8 chars, uppercase, number, symbol" required>
          </div>
          <div class="form-group">
            <label>Confirm Password</label>
            <input type="password" name="confirm" placeholder="Repeat password" required>
          </div>
          <button type="submit" class="btn">Create Account</button>
        </form>
        <hr class="divider">
        <div class="link">Already have an account? <a href="/login">Login</a></div>
      </div>
    </body>
    </html>
    """)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head><title>SecureAuth | Dashboard</title>{BASE_STYLE}</head>
    <body>
      <div class="card dashboard">
        <div class="dash-header">
          <span class="dash-title">Dashboard</span>
          <span class="badge">Authenticated</span>
        </div>
        <div class="info-grid">
          <div class="info-box">
            <div class="label">Logged in as</div>
            <div class="value">{ session['user'] }</div>
          </div>
          <div class="info-box">
            <div class="label">Status</div>
            <div class="value"><span class="status-dot"></span>Active</div>
          </div>
          <div class="info-box">
            <div class="label">Email</div>
            <div class="value" style="font-size:12px">{ session['email'] }</div>
          </div>
          <div class="info-box">
            <div class="label">Auth Method</div>
            <div class="value" style="font-size:12px">SHA-256 + Salt</div>
          </div>
        </div>
        <div class="alert alert-success" style="margin-bottom:20px">
          Login successful. Session active and secured.
        </div>
        <a href="/logout"><button class="btn btn-secondary">Logout</button></a>
      </div>
    </body>
    </html>
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    print("SecureAuth running at http://127.0.0.1:5000")
    app.run(debug=True)