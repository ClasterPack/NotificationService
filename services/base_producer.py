from abc import ABC, abstractmethod


class AbstractQueueProducer(ABC):
    @abstractmethod
    async def send(self, payload: dict):
        pass
