"""TOTP (Google Authenticator) 2FA routes"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services.totp_service import (
    generate_totp_secret_for,
    generate_qr_base64_from_uri,
    set_totp_secret_for_phone,
    verify_totp_token,
    is_totp_enabled
)
from database import get_user_by_email_or_phone

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class TOTPSetupRequest(BaseModel):
    contact: str  # email or phone

class TOTPVerifyRequest(BaseModel):
    token: str

@router.post("/totp/setup")
async def setup_totp(request: Request, data: TOTPSetupRequest):
    """
    Generate TOTP secret and QR code for user
    """
    try:
        contact = data.contact.strip()
        
        # Check if user exists
        user = get_user_by_email_or_phone(contact)
        if not user:
            return JSONResponse(
                {"success": False, "error": "User not found"},
                status_code=404
            )
        
        # Generate secret and URI
        secret, uri = generate_totp_secret_for(contact, "Sports Club")
        
        # Generate QR code
        qr_base64 = generate_qr_base64_from_uri(uri)
        
        # Save secret to database
        set_totp_secret_for_phone(contact, secret)
        
        return JSONResponse({
            "success": True,
            "secret": secret,
            "qr_code": qr_base64,
            "uri": uri
        })
    
    except Exception as e:
        print(f"ERROR in setup_totp: {str(e)}")
        return JSONResponse(
            {"success": False, "error": "Failed to setup TOTP"},
            status_code=500
        )

@router.post("/totp/verify-login")
async def verify_totp_login(request: Request, data: TOTPVerifyRequest):
    """
    Verify TOTP token and complete login
    """
    try:
        token = data.token.strip()
        
        # Get pending login from session
        pending_login = request.session.get("pending_totp_login")
        if not pending_login:
            return JSONResponse(
                {"success": False, "error": "No pending login. Please login again."},
                status_code=400
            )
        
        contact = pending_login.get("contact")
        user_id = pending_login.get("user_id")
        
        # Verify TOTP token
        if not verify_totp_token(contact, token):
            return JSONResponse(
                {"success": False, "error": "Invalid or expired code"},
                status_code=401
            )
        
        # TOTP verified - complete login
        request.session["user_id"] = user_id
        request.session.pop("pending_totp_login", None)
        
        return JSONResponse({
            "success": True,
            "message": "Login successful",
            "redirect": "/sports"
        })
    
    except Exception as e:
        print(f"ERROR in verify_totp_login: {str(e)}")
        return JSONResponse(
            {"success": False, "error": "Verification failed"},
            status_code=500
        )

@router.get("/totp", response_class=HTMLResponse)
async def totp_page(request: Request):
    """
    Display TOTP verification page
    """
    pending_login = request.session.get("pending_totp_login")
    if not pending_login:
        return templates.TemplateResponse("login.html", {"request": request})
    
    return templates.TemplateResponse("totp.html", {
        "request": request,
        "contact": pending_login.get("contact")
    })

@router.get("/totp-setup", response_class=HTMLResponse)
async def totp_setup_page(request: Request):
    """
    Display TOTP setup page after registration
    """
    totp_setup = request.session.get("totp_setup")
    if not totp_setup:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("totp_setup.html", {
        "request": request,
        "email": totp_setup.get("email"),
        "secret": totp_setup.get("secret"),
        "qr_code": totp_setup.get("qr_code")
    })

@router.post("/totp-setup/complete")
async def complete_totp_setup(request: Request):
    """
    Complete TOTP setup and redirect to login
    """
    try:
        # Clear TOTP setup from session
        request.session.pop("totp_setup", None)
        
        return JSONResponse({
            "success": True,
            "message": "2FA setup complete! Please login.",
            "redirect": "/login"
        })
    except Exception as e:
        print(f"ERROR in complete_totp_setup: {str(e)}")
        return JSONResponse(
            {"success": False, "error": "Failed to complete setup"},
            status_code=500
        )

@router.get("/totp/qr")
async def get_totp_qr(request: Request, contact: str):
    """
    Get QR code for existing TOTP setup
    """
    try:
        from services.totp_service import get_totp_secret_by_phone
        
        secret = get_totp_secret_by_phone(contact)
        if not secret:
            return JSONResponse(
                {"success": False, "error": "TOTP not setup for this user"},
                status_code=404
            )
        
        import pyotp
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=contact, issuer_name="Sports Club")
        qr_base64 = generate_qr_base64_from_uri(uri)
        
        return JSONResponse({
            "success": True,
            "qr_code": qr_base64
        })
    
    except Exception as e:
        print(f"ERROR in get_totp_qr: {str(e)}")
        return JSONResponse(
            {"success": False, "error": "Failed to generate QR code"},
            status_code=500
        )
