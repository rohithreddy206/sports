"""Validation utilities"""
import re

def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    """Basic phone validation - digits only with optional + prefix"""
    pattern = r'^\+?[0-9]{10,15}$'
    normalized = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    return re.match(pattern, normalized) is not None
