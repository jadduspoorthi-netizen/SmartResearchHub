from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from source_code.auth_service import decode_access_token
from source_code.database.user_repository import get_user_by_id


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    Authenticate the current request using a Bearer JWT token.
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)

        user_id = int(payload["sub"])

    except (ValueError, KeyError, TypeError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    Return the current user when a valid token is supplied.
    Return None when no valid authentication is provided.
    """

    if credentials is None:
        return None

    try:
        payload = decode_access_token(credentials.credentials)

        user_id = int(payload["sub"])

    except (ValueError, KeyError, TypeError, Exception):
        return None

    return get_user_by_id(user_id)


def require_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Require the authenticated user to have administrator privileges.
    """

    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator permission required.",
        )

    return current_user