"""Setup TOTP for a user"""
from services.totp_service import generate_totp_secret_for, set_totp_secret_for_phone, generate_qr_base64_from_uri

# Replace with your registered email
email = "johnhhh2022@gmail.com"

try:
    # Generate secret
    secret, uri = generate_totp_secret_for(email, "Sports Club")
    print(f"Secret: {secret}")
    print(f"URI: {uri}")
    
    # Save to database
    set_totp_secret_for_phone(email, secret)
    print(f"✅ TOTP enabled for {email}")
    
    # Generate QR code
    qr_code = generate_qr_base64_from_uri(uri)
    
    # Save QR code to HTML file
    html = f"""
    <html>
    <body style="text-align: center; padding: 50px;">
        <h1>Scan this QR code with Google Authenticator</h1>
        <img src="{qr_code}" />
        <p>Secret: <code>{secret}</code></p>
        <p>Or manually enter this code in your authenticator app</p>
    </body>
    </html>
    """
    
    with open("totp_qr.html", "w") as f:
        f.write(html)
    
    print("✅ QR code saved to totp_qr.html - Open it in your browser!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
