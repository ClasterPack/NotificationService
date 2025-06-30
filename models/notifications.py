import uuid
from typing import Optional
from pydantic import BaseModel

class NotificationIn(BaseModel):
    id: uuid
    event: str
    campaign_id: str
    notification_type: str  # email, sms, push
    subject: str
    text: str
    user_id: Optional[uuid] = None

class Notification(NotificationIn):
    pass