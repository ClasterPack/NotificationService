import asyncio
import json

from aiokafka import AIOKafkaProducer

from core.config import settings

from .queue_producer import AbstractQueueProducer


class KafkaProducer(AbstractQueueProducer):
    def __init__(self):
        self._producer: AIOKafkaProducer | None = None
        self._lock = asyncio.Lock()
        self._initialized = False

    async def _initialize(self):
        async with self._lock:
            if self._initialized:
                return
            self._producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_url)
            await self._producer.start()
            self._initialized = True

    async def send(self, payload: dict):
        if not self._initialized:
            await self._initialize()
        await self._producer.send_and_wait(
            topic=settings.queue_channel,
            value=json.dumps(payload).encode("utf-8"),
        )

    async def close(self):
        if self._producer and self._initialized:
            await self._producer.stop()
            self._initialized = False
