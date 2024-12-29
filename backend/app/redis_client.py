import redis.asyncio as aioredis

_redis_client: aioredis.Redis = aioredis.from_url(url="redis://localhost")


redis_pubsub = _redis_client.pubsub()
