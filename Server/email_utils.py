import os
import time
import random
import string
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db_utils import save_verification_code
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Load SMTP credentials from environment variables
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Function declarations:
# def is_valid_email(email): -> bool
# def send_email(email, subject, body): -> bool
# def generate_verification_code(): -> str
# def generate_reset_token(): -> str
# def send_verification_email(email, verification_code): -> bool
# def send_password_reset_email(email, reset_token): -> bool

def is_valid_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def send_email(email, subject, body):
    """Send email to user"""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("[Server] SMTP credentials are missing!")
        return False
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_EMAIL, email, text)
        server.quit()
        print(f"[Server] Email sent to {email}.")
        return True
    except Exception as e:
        print(f"[Server] Error sending email: {e}")
        return False


def generate_verification_code():
    """Generate 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))


def generate_reset_token():
    """Generate random password reset token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def send_verification_email(email, verification_code):
    """Send verification email with code"""
    current_time = int(time.time())
    expiry_time = current_time + 30 * 60  # Code valid for 30 minutes

    # Store verification code in database
    save_verification_code(email, verification_code, expiry_time)

    return send_email(email, 'Email Verification Code',
                      f"Your verification code is: {verification_code}\nThis code will expire in 30 minutes.")


def send_password_reset_email(email, reset_token):
    """Send password reset token email"""
    return send_email(email, 'Password Reset Request',
                      f"Your password reset token is: {reset_token}\nThis token will expire in 30 minutes.")
