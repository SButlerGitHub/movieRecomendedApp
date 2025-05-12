import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_SERVER

def generate_reset_token():
    """Generate a secure random token for password reset."""
    return secrets.token_urlsafe(32)

def send_reset_email(email, token):
    """Send password reset email."""
    reset_link = f"http://localhost:3000/reset-password/{token}"
    
    message = MIMEMultipart()
    message["From"] = EMAIL_USER
    message["To"] = email
    message["Subject"] = "Password Reset - Film Finder"
    
    body = f"""
    Hello,
    
    You recently requested to reset your password for your Film Finder account.
    
    Please click the link below to reset your password:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you did not request a password reset, please ignore this email.
    
    Best regards,
    The Film Finder Team
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP(EMAIL_SERVER, 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False