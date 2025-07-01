from fastapi import APIRouter, Depends, HTTPException, Query

from core.auth import get_current_user
from core.config import settings
from models.notifications import NotificationIn
from services.queue_producer import queue_producer
from storage.mongo_storage import notifications_collection

router = APIRouter()


@router.post("/notifications/event")
async def receive_event(notification: NotificationIn):
    await queue_producer.send(notification.model_dump())
    await notifications_collection.insert_one(notification.model_dump())
    return {"status": "queued"}


@router.get("/users/{user_id}/notifications")
async def get_user_notifications(
    user_id: str,
    user=Depends(get_current_user),
    limit: int = Query(settings.default_page_limit, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    if user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    notifications = (
        await notifications_collection.find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(offset)
        .limit(limit)
        .to_list(length=None)
    )

    return notifications
