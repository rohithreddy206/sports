"""Phone OTP service using Twilio Verify"""
from fastapi import Request
from fastapi.responses import JSONResponse
from services.sms_service import send_phone_otp, verify_phone_otp

async def send_twilio_phone_otp(request: Request):
    """Send OTP using Twilio Verify API"""
    try:
        data = await request.json()
        phone = data.get("phone", "").strip()
        
        if not phone:
            return JSONResponse(
                {"success": False, "error": "Phone number is required"},
                status_code=400
            )
        
        result = send_phone_otp(phone)
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": result["message"]
            })
        else:
            return JSONResponse(
                {"success": False, "error": result["message"]},
                status_code=500
            )
    
    except Exception as e:
        print(f"ERROR in send_twilio_phone_otp: {str(e)}")
        return JSONResponse(
            {"success": False, "error": "Failed to send OTP"},
            status_code=500
        )

async def verify_twilio_phone_otp(request: Request):
    """Verify OTP using Twilio Verify API"""
    try:
        data = await request.json()
        phone = data.get("phone", "").strip()
        otp = data.get("otp", "").strip()
        
        if not phone or not otp:
            return JSONResponse(
                {"success": False, "error": "Phone and OTP are required"},
                status_code=400
            )
        
        result = verify_phone_otp(phone, otp)
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": result["message"]
            })
        else:
            return JSONResponse(
                {"success": False, "error": result["message"]},
                status_code=400
            )
    
    except Exception as e:
        print(f"ERROR in verify_twilio_phone_otp: {str(e)}")
        return JSONResponse(
            {"success": False, "error": "Verification failed"},
            status_code=500
        )
