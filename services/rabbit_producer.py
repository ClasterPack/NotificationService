from core.logger import logger
from .queue_producer import AbstractQueueProducer

class RabbitProducer(AbstractQueueProducer):
    async def send(self, payload: dict):
        logger.info("Sending to RabbitMQ", payload)
        # Здесь логика отправки в RabbitMQ
        pass