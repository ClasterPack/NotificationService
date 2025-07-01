import uuid

import pytest

from models.notifications import NotificationType


def serialize_payload(payload: dict):
    new_payload = {}
    for k, v in payload.items():
        if k == "id":
            new_payload[k] = uuid.UUID(v)
        elif k == "notification_type":
            new_payload[k] = NotificationType(v)
        elif k == "user_id" and v is not None:
            new_payload[k] = uuid.UUID(v)
        else:
            new_payload[k] = v
    return new_payload


@pytest.mark.asyncio
async def test_post_notification_event(client, mock_queue_producer_send):
    notification_payload = {
        "id": str(uuid.uuid4()),
        "event": "campaign_launch",
        "campaign_id": "camp456",
        "notification_type": "push",
        "subject": "Campaign Started",
        "text": "Our new campaign is live!",
        "user_id": None,
    }

    response = await client.post(
        "/api/v1/notifications/event", json=notification_payload
    )
    assert response.status_code == 200
    assert response.json() == {"status": "queued"}

    mock_queue_producer_send.assert_awaited_once_with(
        serialize_payload(notification_payload)
    )


@pytest.mark.asyncio
async def test_post_notification_event_with_user(client, mock_queue_producer_send):
    user_id = str(uuid.uuid4())
    notification_payload = {
        "id": str(uuid.uuid4()),
        "event": "campaign_launch",
        "campaign_id": "camp789",
        "notification_type": "email",
        "subject": "Email Subject",
        "text": "Email text",
        "user_id": user_id,
    }

    response = await client.post(
        "/api/v1/notifications/event", json=notification_payload
    )
    assert response.status_code == 200
    assert response.json() == {"status": "queued"}

    mock_queue_producer_send.assert_awaited_once_with(
        serialize_payload(notification_payload)
    )


@pytest.mark.asyncio
async def test_get_user_notifications_authorized(
    client, test_user, mock_notifications_collection
):
    user_id = test_user["id"]
    mock_notifications_collection.append(
        {
            "id": str(uuid.uuid4()),
            "event": "some_event",
            "campaign_id": "camp123",
            "notification_type": "email",
            "subject": "Subject",
            "text": "Text",
            "user_id": user_id,
            "created_at": "2025-07-01T00:00:00Z",
        }
    )

    url = f"/api/v1/users/{user_id}/notifications"
    response = await client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["user_id"] == user_id


@pytest.mark.asyncio
async def test_get_user_notifications_forbidden(client, test_user):
    wrong_user_id = str(uuid.uuid4())
    url = f"/api/v1/users/{wrong_user_id}/notifications"
    response = await client.get(url)
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
