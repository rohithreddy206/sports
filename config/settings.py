"""Application configuration and constants"""

# OTP Configuration
OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 3
RATE_LIMIT_MINUTES = 5
MAX_RATE_LIMIT_ATTEMPTS = 3

# Session Configuration
SESSION_SECRET_KEY = "your-secret-key-change-in-production"
