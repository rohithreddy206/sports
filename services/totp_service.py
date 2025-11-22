"""TOTP (Google Authenticator) service"""
import pyotp
import qrcode
import io
import base64
from database import get_connection

def generate_totp_secret_for(contact: str, name: str = "Sports Club") -> tuple:
    """
    Generate TOTP secret and provisioning URI
    
    Args:
        contact: User's email or phone
        name: Application name
    
    Returns:
        tuple: (secret, provisioning_uri)
    """
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=contact, issuer_name=name)
    return secret, uri

def generate_qr_base64_from_uri(uri: str) -> str:
    """
    Generate QR code as base64 string from provisioning URI
    
    Args:
        uri: TOTP provisioning URI
    
    Returns:
        str: Base64 encoded QR code image
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_base64}"

def set_totp_secret_for_phone(contact: str, secret: str):
    """
    Store TOTP secret for user (by email or phone)
    
    Args:
        contact: User's email or phone
        secret: TOTP secret key
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS totp_secrets (
            user_id INTEGER PRIMARY KEY,
            secret TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Get user ID
    cur.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (contact, contact))
    user = cur.fetchone()
    
    if not user:
        conn.close()
        raise ValueError("User not found")
    
    user_id = user["id"]
    
    # Insert or update secret
    cur.execute("""
        INSERT OR REPLACE INTO totp_secrets (user_id, secret, enabled)
        VALUES (?, ?, 1)
    """, (user_id, secret))
    
    conn.commit()
    conn.close()

def get_totp_secret_by_phone(contact: str):
    """
    Retrieve TOTP secret for user
    
    Args:
        contact: User's email or phone
    
    Returns:
        str: TOTP secret or None
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT ts.secret 
            FROM totp_secrets ts
            JOIN users u ON ts.user_id = u.id
            WHERE (u.email = ? OR u.phone = ?) AND ts.enabled = 1
        """, (contact, contact))
        
        result = cur.fetchone()
        conn.close()
        
        return result["secret"] if result else None
    except Exception as e:
        print(f"ERROR in get_totp_secret_by_phone: {str(e)}")
        return None

def verify_totp_token(contact: str, token: str) -> bool:
    """
    Verify TOTP token for user
    
    Args:
        contact: User's email or phone
        token: 6-digit TOTP code
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        secret = get_totp_secret_by_phone(contact)
        if not secret:
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    except Exception as e:
        print(f"ERROR in verify_totp_token: {str(e)}")
        return False

def is_totp_enabled(contact: str) -> bool:
    """
    Check if user has TOTP enabled
    
    Args:
        contact: User's email or phone
    
    Returns:
        bool: True if TOTP enabled, False otherwise
    """
    try:
        return get_totp_secret_by_phone(contact) is not None
    except Exception as e:
        print(f"ERROR in is_totp_enabled: {str(e)}")
        return False
