import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import BinaryExpression, BindParameter

# Mock environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET", "test-secret")

from main import create_app
from db.database import get_db as get_db_db
from db.session import get_db as get_db_session
import utils.security

class FakeQuery:
    def __init__(self, rows, model=None):
        self.rows = list(rows)
        self.model = model

    def filter(self, *expressions):
        filtered_rows = list(self.rows)
        for expr in expressions:
            if not isinstance(expr, BinaryExpression):
                continue
                
            attr_name = None
            if isinstance(expr.left, InstrumentedAttribute):
                attr_name = expr.left.key
            else:
                attr_name = getattr(expr.left, "name", None)
            
            if not attr_name:
                continue

            value = expr.right
            if isinstance(value, BindParameter):
                value = value.value
            
            temp_rows = []
            for r in filtered_rows:
                val_r = getattr(r, attr_name, None)
                
                # Handle UUID vs string comparison for id fields
                if isinstance(val_r, uuid.UUID) and isinstance(value, str):
                    try:
                        if str(val_r) == value:
                            temp_rows.append(r)
                            continue
                    except: pass
                elif isinstance(value, uuid.UUID) and isinstance(val_r, str):
                    try:
                        if str(value) == val_r:
                            temp_rows.append(r)
                            continue
                    except: pass
                
                if val_r == value:
                    temp_rows.append(r)
            filtered_rows = temp_rows
            
        return FakeQuery(filtered_rows, model=self.model)

    def first(self):
        return self.rows[0] if self.rows else None

    def all(self):
        return list(self.rows)

    def order_by(self, *args, **kwargs):
        return self

class FakeDBSession:
    def __init__(self):
        self.storage = {} # model_class -> list of objects
        self.committed = False
        self.closed = False

    def query(self, model):
        if model not in self.storage:
            self.storage[model] = []
        return FakeQuery(self.storage[model], model=model)

    def add(self, instance):
        if not getattr(instance, "id", None):
            instance.id = uuid.uuid4()
        
        model_class = type(instance)
        if model_class not in self.storage:
            self.storage[model_class] = []
        
        if instance not in self.storage[model_class]:
            self.storage[model_class].append(instance)

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def refresh(self, instance):
        pass

    def close(self):
        self.closed = True

@pytest.fixture(autouse=True)
def mock_password_verification(monkeypatch):
    # Mock password verification to always return True for tests
    monkeypatch.setattr(utils.security, "verify_password", lambda p, h: True)

@pytest.fixture
def fake_db():
    return FakeDBSession()

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def client(app, fake_db):
    def override_get_db():
        try:
            yield fake_db
        finally:
            fake_db.close()
    
    # Override both potential get_db references used in controllers and dependencies
    app.dependency_overrides[get_db_db] = override_get_db
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as tc:
        yield tc
    
    app.dependency_overrides.clear()
