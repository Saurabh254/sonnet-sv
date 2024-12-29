import asyncio

import redis
import redis.asyncio.client
import redis.client
from fastapi import HTTPException

from app.redis_client import _redis_client

DRIVER_WEBSOCKET_TOPIC = "driver/location/{driver_id}"
DRIVER_EVENTSOURCE_ENDPOINT = "driver/{driver_id}/new-ride"


class RedisStream:

    def __init__(self, driver_id: str) -> None:
        self.driver_id = driver_id

    async def publish_data_to_topic(self, topic, data):
        await _redis_client.publish(topic, data)

    async def get_published_messages(
        self, topic: str, _redis: redis.asyncio.client.Redis
    ):
        # Create a PubSub object
        pubsub: redis.asyncio.client.PubSub = _redis.pubsub()

        # Subscribe to the topic (await since it's an async operation)
        await pubsub.subscribe(topic)

        # Process messages in an infinite loop
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message and message["type"] == "message":
                    yield {message["data"].decode("utf-8")}
                await asyncio.sleep(0.1)  # Small delay to prevent busy-waiting
        except asyncio.CancelledError:
            # Handle task cancellation if necessary
            print("Listener task was cancelled.")
            raise HTTPException(status_code=403)
        finally:
            # Unsubscribe and close PubSub
            await pubsub.unsubscribe(topic)
            await pubsub.close()
