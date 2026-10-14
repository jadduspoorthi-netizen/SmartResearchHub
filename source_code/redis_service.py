import os
from typing import Optional

import redis
from dotenv import load_dotenv

load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
)


def set_value(
    key: str,
    value: str,
    expiry_seconds: Optional[int] = None,
) -> bool:
    """
    Store a value in Redis.

    If expiry_seconds is provided, Redis automatically
    deletes the value after that many seconds.
    """
    if expiry_seconds is not None:
        return bool(
            redis_client.set(
                key,
                value,
                ex=expiry_seconds,
            )
        )

    return bool(redis_client.set(key, value))


def get_value(key: str) -> Optional[str]:
    """Retrieve a value from Redis."""
    return redis_client.get(key)


def delete_value(key: str) -> bool:
    """Delete a value from Redis."""
    return bool(redis_client.delete(key))


def redis_is_available() -> bool:
    """Check whether Redis is reachable."""
    try:
        redis_client.ping()
        return True
    except redis.RedisError:
        return False