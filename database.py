import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "sports_club.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS email_verifications (
            email TEXT PRIMARY KEY,
            otp TEXT NOT NULL,
            expires_at DATETIME NOT NULL
        );
        """
    )
    # Drop old table if exists and recreate with correct schema
    cur.execute("DROP TABLE IF EXISTS phone_verifications")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS phone_verifications (
            phone TEXT PRIMARY KEY,
            otp TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            attempts INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
    conn.close()

def create_user(first_name, last_name, email, phone, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (first_name, last_name, email, phone, password_hash) VALUES (?, ?, ?, ?, ?)",
        (first_name, last_name, email.lower().strip(), phone.strip(), password_hash),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id

def get_user_by_email_or_phone(identifier):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE email = ? OR phone = ?",
        (identifier.lower().strip(), identifier.strip()),
    )
    row = cur.fetchone()
    conn.close()
    return row

def get_user_by_id(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

# Email verification functions
def store_otp(email: str, otp: str, expires_at: datetime):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO email_verifications (email, otp, expires_at) VALUES (?, ?, ?)",
        (email.lower().strip(), otp, expires_at.isoformat()),
    )
    conn.commit()
    conn.close()

def get_otp(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT otp, expires_at FROM email_verifications WHERE email = ?",
        (email.lower().strip(),),
    )
    row = cur.fetchone()
    conn.close()
    return row

def delete_otp(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM email_verifications WHERE email = ?", (email.lower().strip(),))
    conn.commit()
    conn.close()

# Phone verification functions
def save_phone_otp(phone: str, otp: str, expires_at: datetime):
    """
    Save or update phone OTP with expiry time
    """
    conn = get_connection()
    cur = conn.cursor()
    # Use current timestamp for created_at when inserting/replacing
    cur.execute(
        "INSERT OR REPLACE INTO phone_verifications (phone, otp, expires_at, attempts, created_at) VALUES (?, ?, ?, 0, ?)",
        (phone.strip(), otp, expires_at.isoformat(), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

def get_phone_otp(phone: str):
    """
    Retrieve phone OTP record
    Returns: dict with otp, expires_at, attempts or None
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT otp, expires_at, attempts FROM phone_verifications WHERE phone = ?",
        (phone.strip(),),
    )
    row = cur.fetchone()
    conn.close()
    return row

def increment_phone_otp_attempts(phone: str):
    """
    Increment verification attempts for a phone number
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE phone_verifications SET attempts = attempts + 1 WHERE phone = ?",
        (phone.strip(),),
    )
    conn.commit()
    conn.close()

def delete_phone_otp(phone: str):
    """
    Delete phone OTP record after successful verification
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM phone_verifications WHERE phone = ?", (phone.strip(),))
    conn.commit()
    conn.close()

def check_phone_rate_limit(phone: str, minutes: int = 5, max_attempts: int = 3) -> bool:
    """
    Check if phone has exceeded rate limit for OTP requests
    Returns True if rate limit exceeded, False otherwise
    """
    conn = get_connection()
    cur = conn.cursor()
    time_threshold = (datetime.now() - timedelta(minutes=minutes)).isoformat()
    
    # Count recent OTP requests for this phone
    cur.execute(
        "SELECT COUNT(*) as count FROM phone_verifications WHERE phone = ? AND created_at > ?",
        (phone.strip(), time_threshold),
    )
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return False
    
    return row["count"] >= max_attempts

# Ensure database is initialized when module is imported
init_db()
