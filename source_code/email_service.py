import os

import resend
from dotenv import load_dotenv

load_dotenv()


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv(
    "RESEND_FROM_EMAIL",
    "onboarding@resend.dev",
)


def send_otp_email(email: str, otp: str) -> bool:
    """
    Send the verification OTP to the user's email.

    The OTP is only used here to construct the email.
    It is never printed to the terminal.
    """

    if not RESEND_API_KEY:
        raise RuntimeError(
            "RESEND_API_KEY is not configured in the .env file."
        )

    resend.api_key = RESEND_API_KEY

    params = {
        "from": RESEND_FROM_EMAIL,
        "to": [email.strip().lower()],
        "subject": "SmartResearch Hub - Email Verification Code",
        "html": f"""
        <div style="
            font-family: Georgia, 'Times New Roman', serif;
            background: #f4efe3;
            padding: 32px;
            color: #283127;
        ">
            <div style="
                max-width: 560px;
                margin: 0 auto;
                background: #fffdf7;
                border: 1px solid #c9c0ad;
                padding: 32px;
            ">
                <h1 style="
                    margin-top: 0;
                    color: #3f4a38;
                    font-size: 28px;
                ">
                    SmartResearch Hub
                </h1>

                <p style="font-size: 16px; line-height: 1.6;">
                    Welcome to SmartResearch Hub.
                    Use the verification code below to complete
                    your account registration.
                </p>

                <div style="
                    margin: 28px 0;
                    padding: 18px;
                    text-align: center;
                    background: #ece6d8;
                    border: 1px solid #b8ae99;
                ">
                    <span style="
                        font-family: 'Courier New', monospace;
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        color: #283127;
                    ">
                        {otp}
                    </span>
                </div>

                <p style="
                    font-size: 14px;
                    line-height: 1.6;
                    color: #625f55;
                ">
                    This verification code expires in 5 minutes.
                    If you did not request this code, you can safely
                    ignore this email.
                </p>

                <hr style="
                    border: 0;
                    border-top: 1px solid #d5cdbc;
                    margin: 28px 0;
                ">

                <p style="
                    margin-bottom: 0;
                    font-size: 13px;
                    color: #777064;
                ">
                    SmartResearch Hub<br>
                    AI-Powered Semantic Knowledge Repository
                </p>
            </div>
        </div>
        """,
    }

    try:
        resend.Emails.send(params)
        return True
    except Exception as error:
        print(f"Email delivery failed: {error}")
        return False