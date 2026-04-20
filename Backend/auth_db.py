import sqlite3
import os
import hashlib

BASE_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(BASE_DIR, "users.db")

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_users_db():
    """Initialize the users database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_user(username: str, password: str) -> bool:
    """Create a new user. Returns True if successful, False if username exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Username already exists
    finally:
        conn.close()
        
    return success

def verify_user(username: str, password: str) -> bool:
    """Verify user credentials."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password_hash))
    user = cursor.fetchone()
    
    conn.close()
    
    return user is not None

# Initialize on import
init_users_db()
