import redis.asyncio as aioredis


def get_redis_conn_dep() -> aioredis.Redis:
    connection = aioredis.Redis()
    return connection
