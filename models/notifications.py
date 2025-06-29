from typing import Optional
from pydantic import BaseModel

class NotificationIn(BaseModel):
    id: str
    event: str
    template_id: str
    notification_type: str  # email, sms, push
    subject: str
    text: str
    user_id: Optional[str] = None

class Notification(NotificationIn):
    pass