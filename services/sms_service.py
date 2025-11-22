import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio configuration from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Twilio Verify Service SID
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

def send_sms(phone: str, message: str) -> bool:
    """
    Send SMS using Twilio
    
    Args:
        phone: Recipient phone number (E.164 format recommended, e.g., +1234567890)
        message: SMS message content
    
    Returns:
        True if SMS sent successfully, False otherwise
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("ERROR: Twilio credentials not configured in environment variables")
        return False
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send SMS
        message_obj = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        
        # Log success (do NOT log OTP in production)
        print(f"SMS sent successfully. SID: {message_obj.sid}, Status: {message_obj.status}")
        return True
        
    except Exception as e:
        # Log error but do not expose details to user
        print(f"ERROR sending SMS to {phone}: {str(e)}")
        return False

def send_phone_otp_sms(phone: str, otp: str) -> bool:
    """
    Send phone verification OTP via SMS
    
    Args:
        phone: Recipient phone number
        otp: 6-digit OTP code
    
    Returns:
        True if sent successfully, False otherwise
    """
    message = f"Your Sports Club verification code is: {otp}\n\nThis code will expire in 5 minutes.\n\nIf you didn't request this, please ignore this message."
    return send_sms(phone, message)

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

def send_phone_otp(phone_number: str) -> dict:
    """
    Send OTP to phone number using Twilio Verify API
    
    Args:
        phone_number: Phone number in E.164 format (e.g., +1234567890)
    
    Returns:
        dict: {"success": bool, "message": str, "sid": str (optional)}
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID]):
        print("ERROR: Twilio Verify credentials not configured")
        return {"success": False, "message": "Twilio Verify not configured"}
    
    try:
        from utils.formatting import normalize_phone_number
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        phone_number = normalize_phone_number(phone_number)
        
        verification = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
            .verifications \
            .create(to=phone_number, channel='sms')
        
        print(f"OTP sent via Twilio Verify. Status: {verification.status}, SID: {verification.sid}")
        
        return {
            "success": True,
            "message": f"OTP sent to {phone_number}",
            "sid": verification.sid
        }
        
    except Exception as e:
        print(f"ERROR sending OTP via Twilio Verify: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to send OTP: {str(e)}"
        }

def verify_phone_otp(phone_number: str, otp_code: str) -> dict:
    """
    Verify OTP code using Twilio Verify API
    
    Args:
        phone_number: Phone number in E.164 format
        otp_code: 6-digit OTP code entered by user
    
    Returns:
        dict: {"success": bool, "message": str, "status": str (optional)}
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID]):
        print("ERROR: Twilio Verify credentials not configured")
        return {"success": False, "message": "Twilio Verify not configured"}
    
    try:
        from utils.formatting import normalize_phone_number
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        phone_number = normalize_phone_number(phone_number)
        
        verification_check = client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID) \
            .verification_checks \
            .create(to=phone_number, code=otp_code)
        
        print(f"OTP verification status: {verification_check.status}")
        
        if verification_check.status == "approved":
            return {
                "success": True,
                "message": "Phone verified successfully",
                "status": verification_check.status
            }
        else:
            return {
                "success": False,
                "message": "Invalid OTP code",
                "status": verification_check.status
            }
        
    except Exception as e:
        print(f"ERROR verifying OTP: {str(e)}")
        return {
            "success": False,
            "message": f"Verification failed: {str(e)}"
        }
