"""OTP generation utilities"""
import random

def generate_otp() -> str:
    """Generate 6-digit numeric OTP"""
    return str(random.randint(100000, 999999))
