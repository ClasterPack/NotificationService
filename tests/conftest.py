import uuid
from typing import List
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from core.auth import get_current_user as original_get_current_user
from main import app
from models.notifications import NotificationType
from services.queue_producer import queue_producer
from storage.mongo_storage import notifications_collection


@pytest.fixture
def test_user():
    return {"id": str(uuid4())}


@pytest.fixture(autouse=True)
def override_get_current_user(test_user):
    async def mock_get_current_user():
        return test_user

    app.dependency_overrides[original_get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.pop(original_get_current_user, None)


class FakeCursor:
    def __init__(self, items: List[dict]):
        self._items = items
        self._sort_key = None
        self._sort_reverse = False
        self._skip = 0
        self._limit = None

    def sort(self, key, direction):
        self._sort_key = key
        self._sort_reverse = direction == -1
        return self

    def skip(self, count):
        self._skip = count
        return self

    def limit(self, count):
        self._limit = count
        return self

    async def to_list(self, length=None):
        items = self._items

        if self._sort_key:
            items = sorted(
                items,
                key=lambda x: x.get(self._sort_key),
                reverse=self._sort_reverse,
            )
        if self._skip:
            items = items[self._skip :]
        if self._limit is not None:
            items = items[: self._limit]

        return items


@pytest.fixture(autouse=True)
def mock_notifications_collection(monkeypatch):
    fake_db = []

    async def fake_insert_one(document):
        doc_copy = {}
        for k, v in document.items():
            if isinstance(v, uuid.UUID):
                doc_copy[k] = str(v)
            elif isinstance(v, NotificationType):
                doc_copy[k] = v.value
            else:
                doc_copy[k] = v

        fake_db.append(doc_copy)

        class InsertOneResult:
            inserted_id = doc_copy.get("_id", None)

        return InsertOneResult()

    def fake_find(filter_dict):
        filtered = [
            item
            for item in fake_db
            if item.get("user_id") == filter_dict.get("user_id")
        ]
        return FakeCursor(filtered)

    monkeypatch.setattr(notifications_collection, "insert_one", fake_insert_one)
    monkeypatch.setattr(notifications_collection, "find", fake_find)

    yield fake_db


@pytest.fixture
def mock_queue_producer_send(monkeypatch):
    mock_send = AsyncMock()
    monkeypatch.setattr(queue_producer, "send", mock_send)
    yield mock_send


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    headers = {"Authorization": "Bearer faketoken123"}
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=headers
    ) as ac:
        yield ac
