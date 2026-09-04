import redis
from typing import Optional
from app.core.config import settings

# Redis client
redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """
    Get Redis client
    """
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


def init_redis():
    """
    Initialize Redis connection
    """
    global redis_client
    redis_client = get_redis()
    # Test connection
    redis_client.ping()
