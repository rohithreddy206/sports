"""Authentication routes (login/register/check email)"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from database import get_user_by_email_or_phone, create_user
from utils.validators import is_valid_email
from services.totp_service import is_totp_enabled

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login")
async def login_submit(request: Request):
    data = await request.json()
    identifier = data.get("identifier", "").strip()
    password = data.get("password", "")
    
    if not identifier or not password:
        return JSONResponse({"success": False, "error": "All fields are required"}, status_code=400)
    
    user = get_user_by_email_or_phone(identifier)
    if not user or not pwd_context.verify(password, user["password_hash"]):
        return JSONResponse({"success": False, "error": "Invalid email/phone or password"}, status_code=401)
    
    # Check if user has TOTP enabled
    if is_totp_enabled(identifier):
        # Store pending login in session
        request.session["pending_totp_login"] = {
            "contact": identifier,
            "user_id": user["id"]
        }
        
        return JSONResponse({
            "success": True,
            "require_totp": True,
            "message": "Please enter your 2FA code",
            "redirect": "/totp"
        })
    
    # No TOTP - complete login directly
    request.session["user_id"] = user["id"]
    return JSONResponse({"success": True, "redirect": "/sports"})

@router.get("/check-email")
async def check_email_availability(email: str):
    """Check if email is already registered"""
    try:
        email = email.strip().lower()
        
        if not email or not is_valid_email(email):
            return JSONResponse(
                {"exists": False, "available": False, "message": "Invalid email format"},
                status_code=400
            )
        
        existing_user = get_user_by_email_or_phone(email)
        
        if existing_user:
            return JSONResponse({
                "exists": True,
                "available": False,
                "message": "Email already registered"
            })
        else:
            return JSONResponse({
                "exists": False,
                "available": True,
                "message": "Email available"
            })
    
    except Exception as e:
        print(f"ERROR in check_email_availability: {str(e)}")
        return JSONResponse(
            {"exists": False, "available": False, "message": "Error checking email"},
            status_code=500
        )

@router.post("/verify_phone_otp_and_register")
async def verify_phone_otp_and_register(request: Request):
    """Verify phone OTP and register user"""
    from services.registration_service import complete_registration
    return await complete_registration(request)

@router.post("/register")
async def register_user(request: Request):
    """Register a new user"""
    data = await request.json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()
    
    if not email or not password or not phone:
        return JSONResponse({"success": False, "error": "All fields are required"}, status_code=400)
    
    if not is_valid_email(email):
        return JSONResponse({"success": False, "error": "Invalid email format"}, status_code=400)
    
    # Check if user already exists
    existing_user = get_user_by_email_or_phone(email)
    if existing_user:
        return JSONResponse({"success": False, "error": "Email already registered"}, status_code=409)
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    # Create the user in the database
    try:
        user_id = create_user(email=email, password_hash=hashed_password, phone=phone)
    except Exception as e:
        print(f"ERROR in register_user: {str(e)}")
        return JSONResponse({"success": False, "error": "Failed to register user"}, status_code=500)
    
    return JSONResponse({"success": True, "user_id": user_id, "redirect": "/sports"})
