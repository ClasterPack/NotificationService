from .queue_producer import AbstractQueueProducer
from core.logger import logger

class KafkaProducer(AbstractQueueProducer):
    async def send(self, payload: dict):
        logger.info("Sending to Kafka", payload)
        # Здесь логика отправки в Kafka
        pass