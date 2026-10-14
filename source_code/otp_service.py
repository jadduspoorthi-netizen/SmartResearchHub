import hashlib
import hmac
import os
import secrets
from typing import Optional

from source_code.redis_service import (
    delete_value,
    get_value,
    set_value,
)


OTP_EXPIRY_SECONDS = max(
    60,
    int(os.getenv("OTP_EXPIRY_SECONDS", "300")),
)

OTP_RESEND_COOLDOWN_SECONDS = 60

OTP_KEY_PREFIX = "smartresearchhub:otp:"
COOLDOWN_KEY_PREFIX = "smartresearchhub:otp:cooldown:"


def _normalize_email(email: str) -> str:
    """Normalize an email address consistently."""
    return str(email).strip().lower()


def _normalize_otp(otp: str) -> str:
    """
    Normalize OTP input.

    Removes accidental spaces/newlines while preserving
    leading zeros.
    """
    return "".join(str(otp).split())


def _otp_key(email: str) -> str:
    """Return the Redis key used to store the OTP hash."""
    return f"{OTP_KEY_PREFIX}{_normalize_email(email)}"


def _cooldown_key(email: str) -> str:
    """Return the Redis key used for resend cooldown."""
    return f"{COOLDOWN_KEY_PREFIX}{_normalize_email(email)}"


def _hash_otp(otp: str) -> str:
    """Create a SHA-256 hash of the OTP."""
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def generate_otp() -> str:
    """
    Generate a cryptographically secure six-digit OTP.

    Leading zeroes are preserved because the result is a string.
    """
    return f"{secrets.randbelow(1_000_000):06d}"


def can_send_otp(email: str) -> bool:
    """
    Return True if a new OTP can be sent.
    """
    email = _normalize_email(email)

    if not email:
        return False

    cooldown_key = _cooldown_key(email)

    try:
        return get_value(cooldown_key) is None
    except Exception as error:
        print(
            "OTP DEBUG - Redis error while checking cooldown:",
            error,
        )
        return False


def create_otp(email: str) -> Optional[str]:
    """
    Generate an OTP, store only its hash in Redis,
    and return the plaintext OTP to the email service.

    The plaintext OTP is never logged.
    """

    email = _normalize_email(email)

    if not email:
        return None

    if not can_send_otp(email):
        print(
            "OTP DEBUG - OTP resend blocked by cooldown."
        )
        return None

    otp = generate_otp()
    otp_hash = _hash_otp(otp)

    otp_key = _otp_key(email)
    cooldown_key = _cooldown_key(email)

    try:
        stored = set_value(
            key=otp_key,
            value=otp_hash,
            expiry_seconds=OTP_EXPIRY_SECONDS,
        )
    except Exception as error:
        print(
            "OTP DEBUG - Redis error while storing OTP:",
            error,
        )
        return None

    print("OTP DEBUG - email:", email)
    print("OTP DEBUG - OTP stored:", stored)
    print("OTP DEBUG - OTP hash stored:", otp_hash)
    print(
        "OTP DEBUG - OTP expiry:",
        OTP_EXPIRY_SECONDS,
        "seconds",
    )

    if not stored:
        return None

    try:
        cooldown_stored = set_value(
            key=cooldown_key,
            value="1",
            expiry_seconds=OTP_RESEND_COOLDOWN_SECONDS,
        )
    except Exception as error:
        print(
            "OTP DEBUG - Redis error while storing cooldown:",
            error,
        )
        delete_value(otp_key)
        return None

    if not cooldown_stored:
        delete_value(otp_key)
        return None

    return otp


def verify_otp(
    email: str,
    otp: str,
) -> bool:
    """
    Verify an OTP.

    The OTP is considered valid only when:
    - email exists
    - OTP contains exactly 6 digits
    - Redis still contains the OTP
    - supplied OTP hash matches the stored hash

    A successfully verified OTP is immediately deleted.
    """

    email = _normalize_email(email)
    otp = _normalize_otp(otp)

    print("OTP DEBUG - verifying email:", email)
    print("OTP DEBUG - entered OTP length:", len(otp))
    print(
        "OTP DEBUG - entered OTP contains only digits:",
        otp.isdigit(),
    )

    if not email:
        print("OTP DEBUG - verification failed: empty email")
        return False

    if not otp.isdigit():
        print(
            "OTP DEBUG - verification failed: OTP is not numeric"
        )
        return False

    if len(otp) != 6:
        print(
            "OTP DEBUG - verification failed: OTP is not 6 digits"
        )
        return False

    otp_key = _otp_key(email)

    try:
        stored_hash: Optional[str] = get_value(otp_key)
    except Exception as error:
        print(
            "OTP DEBUG - Redis error while retrieving OTP:",
            error,
        )
        return False

    print(
        "OTP DEBUG - Redis OTP exists:",
        stored_hash is not None,
    )

    if stored_hash is None:
        print(
            "OTP DEBUG - verification failed: "
            "OTP missing or expired"
        )
        return False

    print(
        "OTP DEBUG - Redis hash length:",
        len(stored_hash),
    )

    supplied_hash = _hash_otp(otp)

    hashes_match = hmac.compare_digest(
        stored_hash.strip(),
        supplied_hash,
    )

    print(
        "OTP DEBUG - hashes match:",
        hashes_match,
    )

    if not hashes_match:
        print(
            "OTP DEBUG - verification failed: "
            "incorrect OTP"
        )
        return False

    # OTP is correct.
    # Delete it immediately so it cannot be reused.
    delete_value(otp_key)
    delete_value(_cooldown_key(email))

    print(
        "OTP DEBUG - verification successful"
    )

    return True


def clear_otp(email: str) -> None:
    """
    Completely remove OTP and cooldown information
    for an email address.
    """

    email = _normalize_email(email)

    if not email:
        return

    delete_value(_otp_key(email))
    delete_value(_cooldown_key(email))

    print(
        "OTP DEBUG - OTP cleared for:",
        email,
    )