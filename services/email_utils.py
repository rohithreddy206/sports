import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your_app_password")
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_FROM = os.getenv("MAIL_FROM", "your_email@gmail.com")

def send_email(to: str, subject: str, body: str) -> bool:
    """
    Send email using SMTP
    Returns True if successful, False otherwise
    """
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = MAIL_FROM
        message["To"] = to
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #4f46e5; margin-bottom: 20px;">🏆 Sports Club - Email Verification</h2>
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        {body}
                    </p>
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px;">
                        <p>This OTP will expire in 5 minutes.</p>
                        <p>If you didn't request this, please ignore this email.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        part = MIMEText(html_body, "html")
        message.attach(part)
        
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_otp_email(to: str, otp: str) -> bool:
    """
    Send OTP verification email
    """
    subject = "Verify Your Email - Sports Club"
    body = f"""
        Thank you for registering with Sports Club!
        <br><br>
        Your verification code is:
        <br><br>
        <div style="background-color: #f3f4f6; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
            <span style="font-size: 32px; font-weight: bold; color: #4f46e5; letter-spacing: 8px;">{otp}</span>
        </div>
        <br>
        Please enter this code on the verification page to complete your registration.
    """
    return send_email(to, subject, body)