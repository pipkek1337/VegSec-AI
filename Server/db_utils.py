import sqlite3
import os
import time

DATABASE = 'user_data.db'

# Function prototypes:
# def init_db(): -> None
# def username_exists(username: str) -> bool
# def email_exists(email: str) -> bool
# def save_user(username: str, hashed_pw: str, email: str, verified: int = 0) -> None
# def get_user_by_username(username: str) -> tuple | None
# def get_user_by_email(email: str) -> tuple | None
# def save_verification_code(email: str, code: str, expiry: int) -> None
# def get_verification_code(email: str) -> tuple | None
# def mark_account_verified(email: str) -> None
# def delete_verification_code(email: str) -> None
# def save_reset_token(username: str, reset_token: str, expiry_time: int) -> None
# def get_reset_token(username: str) -> tuple | None
# def update_password(username: str, hashed_pw: str) -> None
# def save_image_cache(image_hash: str, username: str, answer: str, file_path: str) -> None

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    email TEXT,
                    reset_token TEXT,
                    token_expiry INTEGER,
                    verified INTEGER DEFAULT 0
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS verification_codes (
                    email TEXT PRIMARY KEY,
                    code TEXT,
                    expiry INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS image_cache (
                    image_hash TEXT PRIMARY KEY,
                    username TEXT,
                    question TEXT,
                    answer TEXT,
                    file_path TEXT,
                    timestamp INTEGER
                )''')
    # Add a unique index on email to enforce uniqueness at the database level
    c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)''')

    # Check and add timestamp column if not exists
    c.execute("PRAGMA table_info(image_cache)")
    columns = [column[1] for column in c.fetchall()]
    if 'timestamp' not in columns:
        c.execute("ALTER TABLE image_cache ADD COLUMN timestamp INTEGER")

    conn.commit()
    conn.close()
    print("[Server] Database initialized.")


def username_exists(username):
    """Check if a username already exists in the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def email_exists(email):
    """Check if an email already exists in the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE email=?", (email,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def save_user(username, hashed_pw, email, verified=0):
    """Save a new user to the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password_hash, email, verified) VALUES (?, ?, ?, ?)",
              (username, hashed_pw, email, verified))
    conn.commit()
    conn.close()


def get_user_by_username(username):
    """Get user data by username"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT password_hash, verified, email FROM users WHERE username=?", (username,))
    user_data = c.fetchone()
    conn.close()
    return user_data


def get_user_by_email(email):
    """Get user data by email"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE email=?", (email,))
    user_data = c.fetchone()
    conn.close()
    return user_data


def save_verification_code(email, code, expiry):
    """Save verification code to database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO verification_codes (email, code, expiry) VALUES (?, ?, ?)",
              (email, code, expiry))
    conn.commit()
    conn.close()


def get_verification_code(email):
    """Get verification code for email"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT code, expiry FROM verification_codes WHERE email=?", (email,))
    verification_data = c.fetchone()
    conn.close()
    return verification_data


def mark_account_verified(email):
    """Mark user account as verified"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET verified=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()


def delete_verification_code(email):
    """Delete verification code after use"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM verification_codes WHERE email=?", (email,))
    conn.commit()
    conn.close()


def save_reset_token(username, reset_token, expiry_time):
    """Save password reset token"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET reset_token=?, token_expiry=? WHERE username=?",
              (reset_token, expiry_time, username))
    conn.commit()
    conn.close()


def get_reset_token(username):
    """Get reset token data for username"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT reset_token, token_expiry FROM users WHERE username=?", (username,))
    token_data = c.fetchone()
    conn.close()
    return token_data


def update_password(username, hashed_pw):
    """Update user password and clear reset token"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash=?, reset_token=NULL, token_expiry=NULL WHERE username=?",
              (hashed_pw, username))
    conn.commit()
    conn.close()


def save_image_cache(image_hash, username, question, answer, file_path):
    """Save image and answer to cache with timestamp"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO image_cache 
        (image_hash, username, question, answer, file_path, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (image_hash, username, question, answer or "", file_path, int(time.time())))  # Handle None answers
    conn.commit()
    conn.close()