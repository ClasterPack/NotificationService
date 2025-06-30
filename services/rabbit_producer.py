import asyncio
import json

import aio_pika

from core.config import settings

from .queue_producer import AbstractQueueProducer


class RabbitProducer(AbstractQueueProducer):
    def __init__(self):
        self._connection = None
        self._channel = None
        self._exchange = None
        self._lock = asyncio.Lock()
        self._initialized = False

    async def _initialize(self):
        async with self._lock:
            if self._initialized:
                return
            self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                settings.queue_channel, aio_pika.ExchangeType.FANOUT
            )
            self._initialized = True

    async def send(self, payload: dict):
        if not self._initialized:
            await self._initialize()
        message = aio_pika.Message(body=json.dumps(payload).encode("utf-8"))
        await self._exchange.publish(message, routing_key="")
