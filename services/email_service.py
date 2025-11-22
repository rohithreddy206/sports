"""Email OTP service"""
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from database import store_otp, get_otp, delete_otp, get_user_by_email_or_phone
from services.email_utils import send_otp_email  # Updated import
from utils.otp import generate_otp
from utils.validators import is_valid_email

async def send_registration_otp(request: Request):
    """Send email OTP for registration"""
    data = await request.json()
    required_fields = ["first_name", "last_name", "email", "phone", "password", "confirm_password"]
    
    if any(not data.get(field) for field in required_fields):
        return JSONResponse({"success": False, "error": "All fields are required"}, status_code=400)
    
    if data["password"] != data["confirm_password"]:
        return JSONResponse({"success": False, "error": "Passwords do not match"}, status_code=400)
    
    if len(data["password"]) < 6:
        return JSONResponse({"success": False, "error": "Password must be at least 6 characters"}, status_code=400)
    
    email = data["email"].strip()
    
    if not is_valid_email(email):
        return JSONResponse({"success": False, "error": "Invalid email format"}, status_code=400)
    
    # Check BEFORE sending OTP
    if get_user_by_email_or_phone(email):
        return JSONResponse({"success": False, "error": "Email already registered. Please login instead."}, status_code=400)
    
    if get_user_by_email_or_phone(data["phone"]):
        return JSONResponse({"success": False, "error": "Phone already registered. Please login instead."}, status_code=400)
    
    otp = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=5)
    
    try:
        store_otp(email, otp, expires_at)
    except Exception as e:
        return JSONResponse({"success": False, "error": "Failed to generate OTP"}, status_code=500)
    
    if not send_otp_email(email, otp):
        return JSONResponse({"success": False, "error": "Failed to send verification email"}, status_code=500)
    
    request.session["pending_registration"] = {
        "first_name": data["first_name"].strip(),
        "last_name": data["last_name"].strip(),
        "email": email.lower(),
        "phone": data["phone"].strip(),
        "password": data["password"]
    }
    
    return JSONResponse({"success": True, "redirect": "/email_otp"})

async def verify_registration_otp(request: Request):
    """Verify email OTP - DON'T create user yet"""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    data = await request.json()
    otp_input = data.get("otp", "").strip()
    
    if not otp_input:
        return JSONResponse({"success": False, "error": "OTP is required"}, status_code=400)
    
    pending_reg = request.session.get("pending_registration")
    if not pending_reg:
        return JSONResponse({"success": False, "error": "Registration session expired. Please register again."}, status_code=400)
    
    email = pending_reg["email"]
    otp_record = get_otp(email)
    if not otp_record:
        return JSONResponse({"success": False, "error": "OTP not found. Please request a new one."}, status_code=400)
    
    stored_otp = otp_record["otp"]
    expires_at = datetime.fromisoformat(otp_record["expires_at"])
    
    if datetime.now() > expires_at:
        delete_otp(email)
        return JSONResponse({"success": False, "error": "OTP has expired. Please register again."}, status_code=400)
    
    if otp_input != stored_otp:
        return JSONResponse({"success": False, "error": "Invalid OTP. Please try again."}, status_code=400)
    
    # Email OTP verified - just clean up and mark as verified
    delete_otp(email)
    request.session["email_verified"] = True
    
    # DON'T create user here - wait for phone verification
    return JSONResponse({
        "success": True, 
        "redirect": "/register",  # Go back to registration page to verify phone
        "message": "Email verified! Please verify your phone."
    })

async def resend_registration_otp(request: Request):
    """Resend email OTP"""
    pending_reg = request.session.get("pending_registration")
    if not pending_reg:
        return JSONResponse({"success": False, "error": "Registration session expired"}, status_code=400)
    
    email = pending_reg["email"]
    otp = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=5)
    
    store_otp(email, otp, expires_at)
    
    if not send_otp_email(email, otp):
        return JSONResponse({"success": False, "error": "Failed to send email"}, status_code=500)
    
    return JSONResponse({"success": True, "message": "OTP resent successfully"})
