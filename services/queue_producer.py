from core.config import settings
from .base_producer import AbstractQueueProducer
from .kafka_producer import KafkaProducer
from .rabbit_producer import RabbitProducer

# Выбор реализации
if settings.queue_producer.lower() == "kafka":
    queue_producer: AbstractQueueProducer = KafkaProducer()
elif settings.queue_producer.lower() == "rabbitmq":
    queue_producer: AbstractQueueProducer = RabbitProducer()
else:
    raise RuntimeError(f"Unsupported queue_producer: {settings.queue_producer}")
