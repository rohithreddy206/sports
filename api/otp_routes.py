"""Email OTP routes"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from services.email_service import send_registration_otp, verify_registration_otp, resend_registration_otp

router = APIRouter()

@router.post("/send_email_otp")
async def send_email_otp(request: Request):
    """Send email OTP for registration"""
    return await send_registration_otp(request)

@router.post("/verify_email_otp")
async def verify_email_otp(request: Request):
    """Verify email OTP"""
    return await verify_registration_otp(request)

@router.post("/resend_otp")
async def resend_otp(request: Request):
    """Resend email OTP"""
    return await resend_registration_otp(request)
