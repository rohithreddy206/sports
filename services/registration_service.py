"""Registration completion service"""
from fastapi import Request
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from datetime import datetime
from database import create_user, get_user_by_email_or_phone
from utils.validators import is_valid_email, is_valid_phone
from utils.formatting import normalize_phone_number
from services.totp_service import generate_totp_secret_for, set_totp_secret_for_phone, generate_qr_base64_from_uri

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def complete_registration(request: Request):
    """Verify phone OTP and register user - Setup TOTP after registration"""
    try:
        data = await request.json()
        
        required_fields = ["first_name", "last_name", "email", "phone", "password", "confirm_password"]
        
        for field in required_fields:
            if not data.get(field):
                return JSONResponse(
                    {"success": False, "error": f"{field.replace('_', ' ').title()} is required"}, 
                    status_code=400
                )
        
        first_name = data["first_name"].strip()
        last_name = data["last_name"].strip()
        email = data["email"].strip().lower()
        phone = data["phone"].strip()
        password = data["password"]
        confirm_password = data["confirm_password"]
        
        if password != confirm_password:
            return JSONResponse(
                {"success": False, "error": "Passwords do not match"}, 
                status_code=400
            )
        
        if len(password) < 6:
            return JSONResponse(
                {"success": False, "error": "Password must be at least 6 characters long"}, 
                status_code=400
            )
        
        if not is_valid_email(email):
            return JSONResponse(
                {"success": False, "error": "Invalid email format"}, 
                status_code=400
            )
        
        if not is_valid_phone(phone):
            return JSONResponse(
                {"success": False, "error": "Invalid phone number format"}, 
                status_code=400
            )
        
        phone = normalize_phone_number(phone)
        
        # Create user account directly (already verified via OTP)
        try:
            password_hash = pwd_context.hash(password)
            user_id = create_user(first_name, last_name, email, phone, password_hash)
            
            # Generate TOTP secret and QR code for new user
            secret, uri = generate_totp_secret_for(email, "Sports Club")
            qr_code = generate_qr_base64_from_uri(uri)
            
            # Save TOTP secret to database
            set_totp_secret_for_phone(email, secret)
            
            # Store TOTP info in session to show on next page
            request.session["totp_setup"] = {
                "email": email,
                "secret": secret,
                "qr_code": qr_code
            }
            
            return JSONResponse({
                "success": True, 
                "message": "Registration successful! Setting up 2FA...",
                "redirect": "/totp-setup"
            })
            
        except Exception as e:
            error_msg = str(e)
            print(f"ERROR creating user: {error_msg}")
            
            # Handle unique constraint violation
            if "UNIQUE constraint failed" in error_msg:
                if "email" in error_msg:
                    return JSONResponse(
                        {"success": False, "error": "This email is already registered. Please login instead."}, 
                        status_code=400
                    )
                elif "phone" in error_msg:
                    return JSONResponse(
                        {"success": False, "error": "This phone number is already registered. Please login instead."}, 
                        status_code=400
                    )
            
            return JSONResponse(
                {"success": False, "error": "Failed to create account. Please try again."}, 
                status_code=500
            )
    
    except Exception as e:
        print(f"ERROR in complete_registration: {str(e)}")
        return JSONResponse(
            {"success": False, "error": "An error occurred. Please try again."}, 
            status_code=500
        )
