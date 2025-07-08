from flask import Blueprint, request, jsonify
import sqlite3
import os

auth_bp = Blueprint('auth', __name__)

# 🔧 Absolute path to users.db (ensures cross-platform access)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'users.db'))

def connect_db():
    return sqlite3.connect(DB_PATH)

# 🚀 Signup Route
@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'All fields required'}), 400

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Insert user into DB
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, password)
        )
        conn.commit()

        # ✅ Return data for auto-login on frontend
        return jsonify({
            'message': 'User registered successfully',
            'username': username,
            'email': email
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or Email already exists'}), 409
    finally:
        conn.close()

# 🔑 Login Route
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username FROM users WHERE email = ? AND password = ?',
        (email, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            'message': 'Login successful',
            'user_id': user[0],
            'username': user[1]
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
