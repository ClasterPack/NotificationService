import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class NotificationType(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"


class NotificationIn(BaseModel):
    id: uuid.UUID
    event: str
    campaign_id: str
    notification_type: NotificationType
    subject: str
    text: str
    user_id: Optional[uuid.UUID] = None

    model_config = {
        "arbitrary_types_allowed": True,
    }


class Notification(NotificationIn):
    pass
