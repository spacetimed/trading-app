import os

import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUOTE_CACHE_TTL_SECONDS = 60


def get_redis_client():
    return redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )


def build_quote_cache_key(symbol: str) -> str:
    return f"quote:{symbol.strip().upper()}"


def get_cached_quote(symbol: str) -> str | None:
    try:
        return get_redis_client().get(build_quote_cache_key(symbol))
    except redis.RedisError:
        return None


def set_cached_quote(symbol: str, price: str) -> None:
    try:
        get_redis_client().setex(
            build_quote_cache_key(symbol),
            QUOTE_CACHE_TTL_SECONDS,
            price,
        )
    except redis.RedisError:
        return None
