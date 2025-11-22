"""Formatting utilities"""

def normalize_phone_number(phone: str, default_country_code: str = "+1") -> str:
    """
    Normalize phone number format
    
    Args:
        phone: Input phone number
        default_country_code: Default country code if not provided
    
    Returns:
        Normalized phone number in E.164 format
    """
    # Remove spaces, dashes, parentheses
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Add country code if not present
    if not phone.startswith("+"):
        # Remove leading 0 or 1 if present
        if phone.startswith("0"):
            phone = phone[1:]
        elif phone.startswith("1") and len(phone) == 11:
            phone = phone[1:]
        
        phone = default_country_code + phone
    
    return phone
