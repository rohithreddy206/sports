"""Clear a specific user from database"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sports_club.db"

email_to_delete = "johnhhh2022@gmail.com"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Delete user
cur.execute("DELETE FROM users WHERE email = ?", (email_to_delete,))
cur.execute("DELETE FROM email_verifications WHERE email = ?", (email_to_delete,))
cur.execute("DELETE FROM phone_verifications WHERE phone LIKE '%8466968131%'")

conn.commit()
print(f"✅ Deleted user: {email_to_delete}")
conn.close()
