import string
import secrets
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

def generate_otp() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(6))

async def send_verification_email(email_to: EmailStr, otp: str):
    message = MessageSchema(
        subject="Verify your account",
        recipients=[email_to],
        body=f"Your 6-digit verification code is: {otp}. It expires in 15 minutes.",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)


async def send_reset_password_email(email_to: EmailStr, otp: str):
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email_to],
        body=f"Your password reset code is: {otp}. It expires in 15 minutes. If you did not request this, please ignore this email.",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)