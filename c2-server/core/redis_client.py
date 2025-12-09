import redis.asyncio as redis
from core.config import settings

redis_client: redis.Redis = None


async def init_redis():
    global redis_client
    redis_client = await redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    return redis_client


async def get_redis():
    return redis_client


async def close_redis():
    if redis_client:
        await redis_client.close()
