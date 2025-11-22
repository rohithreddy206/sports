import sys
print("Python path:", sys.path)

try:
    from services import sms_service
    print("Module imported successfully")
    print("Available functions:", dir(sms_service))
    print("Has send_phone_otp?", hasattr(sms_service, 'send_phone_otp'))
    print("Has verify_phone_otp?", hasattr(sms_service, 'verify_phone_otp'))
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
