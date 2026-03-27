import os
import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_cache/s2o-api-test.db")
os.environ.setdefault("BASE_URL", "https://testserver")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")

from db.database import get_db
from main import create_app


class FakeQuery:
    def __init__(self, rows):
        self.rows = list(rows)
        self.filters = []

    def filter(self, *conditions):
        self.filters.extend(conditions)
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        return self.rows[0] if self.rows else None

    def all(self):
        return list(self.rows)


class FakeDBSession:
    def __init__(self, query_map=None):
        self.query_map = query_map or {}
        self.added = []
        self.committed = False
        self.refreshed = []
        self.closed = False

    def query(self, model):
        return FakeQuery(self.query_map.get(model, []))

    def add(self, instance):
        if getattr(instance, "id", None) is None:
            instance.id = uuid.uuid4()
        self.added.append(instance)

    def commit(self):
        self.committed = True

    def refresh(self, instance):
        self.refreshed.append(instance)

    def close(self):
        self.closed = True


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def fake_db():
    return FakeDBSession()


@pytest.fixture
def client(app, fake_db):
    def override_get_db():
        try:
            yield fake_db
        finally:
            fake_db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def owner_user():
    return SimpleNamespace(
        id=uuid.uuid4(),
        email="owner@example.com",
        role="owner",
        restaurant_id=None,
    )


@pytest.fixture
def customer_user():
    return SimpleNamespace(
        id=uuid.uuid4(),
        email="customer@example.com",
        role="customer",
        restaurant_id=None,
    )
