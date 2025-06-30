from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings

client = AsyncIOMotorClient(settings.mongo_url)
db = client.bookmark_app
notifications_collection = db["notifications"]
