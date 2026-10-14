import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-to-a-long-random-secret",
)

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "60",
    )
)

ISSUER = "smartresearch-hub"


def hash_password(password: str) -> str:
    """
    Hash a user's password using bcrypt.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """

    if not password or not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    user_id: int,
    username: str,
    role: str,
) -> str:
    """
    Create a JWT access token.
    """

    now = datetime.now(timezone.utc)

    expires_at = (
        now
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": now,
        "exp": expires_at,
        "iss": ISSUER,
        "type": "access",
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    """

    if not token:
        raise ValueError("Access token is required.")

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer=ISSUER,
    )

    if payload.get("type") != "access":
        raise ValueError("Invalid token type.")

    return payload


def validate_password(password: str) -> None:
    """
    Validate password requirements.
    """

    if not password:
        raise ValueError("Password is required.")

    if len(password) < 6:
        raise ValueError(
            "Password must contain at least 6 characters."
        )
