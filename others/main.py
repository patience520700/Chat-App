from flask import Flask, render_template, request, redirect, url_for, jsonify,session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def create_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firebase_uid TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/login')
def index():
    return render_template('login.html')

@app.route('/verify-email')
def verify_email():
    return render_template('verify_email.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', email=session['user_email'])
@app.route('/reset')
def reset():
    return render_template('reset_password.html')

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')



@app.route('/api/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

import requests

@app.route('/api/login', methods=['POST'])
def login():
    id_token = request.json.get('idToken')

    # Verify with Firebase
    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyAfFgHfUpEixyYaz_sSWwTagTNIY8pji88"
    res = requests.post(verify_url, json={'idToken': id_token})

    if res.status_code == 200:
        user_info = res.json()['users'][0]
        if not user_info.get('emailVerified', False):
            return 'Email not verified', 409
        
        user_info = res.json()['users'][0]
        email = user_info['email']
        uid = user_info['localId']

        # Save or update user in SQLite
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE firebase_uid = ?', (uid,)).fetchone()
        if not user:
            conn.execute('INSERT INTO users (firebase_uid, email) VALUES (?, ?)', (uid, email))
            conn.commit()
        conn.close()

        # Login successful
        session['user_email'] = email
        return '', 200
    else:
        return 'Unauthorized', 401



@app.route('/api/register', methods=[ 'POST'])
def registerapi():
    data = request.get_json()
    id_token = data.get('idToken')
    name = data.get('name', '')

    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyAfFgHfUpEixyYaz_sSWwTagTNIY8pji88"
    res = requests.post(verify_url, json={'idToken': id_token})

    if res.status_code != 200:
        return "Invalid token", 401

    
    user_info = res.json()['users'][0]
    email = user_info['email']
    uid = user_info['localId']

    if not user_info.get('emailVerified', False):
        return 'Email not verified', 409
    # Store user in SQLite
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE firebase_uid = ?', (uid,)).fetchone()
    if not user:
        conn.execute(
            'INSERT INTO users (firebase_uid, email, name) VALUES (?, ?, ?)',
            (uid, email, name)
        )
        conn.commit()
    conn.close()

    # Start session
    session['user_email'] = email
    return '', 200

@app.route('/api/verify-email-redirect', methods=['POST'])
def verify_email_redirect():
    data = request.get_json()
    id_token = data.get('idToken')
    verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyAfFgHfUpEixyYaz_sSWwTagTNIY8pji88"
    res = requests.post(verify_url, json={'idToken': id_token})
    if res.status_code != 200:
        return "Invalid token", 401
    user_info = res.json()['users'][0]
    if not user_info.get('emailVerified', False):
        return 'Still not verified', 403
    session['user_email'] = user_info['email']
    return '', 200


if __name__ == '_main_':
    create_users_table()
    app.run(debug=True)