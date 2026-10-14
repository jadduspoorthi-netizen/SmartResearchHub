
from typing import Optional

from source_code.database.connection import get_connection


def get_user_by_username(
    username: str,
) -> Optional[dict]:
    """Get a user by username."""
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    role,
                    plan
                FROM users
                WHERE username = %s
                """,
                (username.strip(),),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "plan": row[5],
            }

    finally:
        conn.close()


def get_user_by_email(
    email: str,
) -> Optional[dict]:
    """Get a user by email address."""
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    role,
                    plan
                FROM users
                WHERE LOWER(email) = LOWER(%s)
                """,
                (email.strip(),),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "plan": row[5],
            }

    finally:
        conn.close()


def get_user_by_id(
    user_id: int,
) -> Optional[dict]:
    """Get a user by ID."""
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    role,
                    plan
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "plan": row[5],
            }

    finally:
        conn.close()


def username_exists(
    username: str,
) -> bool:
    """Check whether a username already exists."""
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM users
                WHERE LOWER(username) = LOWER(%s)
                LIMIT 1
                """,
                (username.strip(),),
            )

            return cursor.fetchone() is not None

    finally:
        conn.close()


def email_exists(
    email: str,
) -> bool:
    """Check whether an email address already exists."""
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM users
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (email.strip(),),
            )

            return cursor.fetchone() is not None

    finally:
        conn.close()


def create_user(
    username: str,
    email: str,
    password_hash: str,
    role: str = "user",
) -> dict:
    """
    Create a new user.
    password_hash must already be hashed before this function is called.
    """
    username = username.strip()
    email = email.strip().lower()
    role = role.strip().lower()

    if not username:
        raise ValueError("Username is required.")

    if not email:
        raise ValueError("Email is required.")

    if not password_hash:
        raise ValueError("Password hash is required.")

    if role not in {"user", "admin"}:
        raise ValueError("Invalid user role.")

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    email,
                    password_hash,
                    role
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING
                    id,
                    username,
                    email,
                    password_hash,
                    role,
                    plan
                """,
                (
                    username,
                    email,
                    password_hash,
                    role,
                ),
            )

            row = cursor.fetchone()

            if row is None:
                raise RuntimeError("User was not created.")

            conn.commit()

            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "password_hash": row[3],
                "role": row[4],
                "plan": row[5],
            }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
