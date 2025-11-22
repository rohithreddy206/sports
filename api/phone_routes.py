"""Phone OTP routes (Twilio Verify)"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from services.phone_service import send_twilio_phone_otp, verify_twilio_phone_otp

router = APIRouter()

@router.post("/send-phone-otp")
async def send_phone_otp_verify(request: Request):
    """Send OTP using Twilio Verify API"""
    return await send_twilio_phone_otp(request)

@router.post("/verify-phone-otp")
async def verify_phone_otp_code(request: Request):
    """Verify OTP using Twilio Verify API"""
    return await verify_twilio_phone_otp(request)
