import os
import tempfile
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base, get_db as database_get_db
from db.session import get_db as session_get_db
from controllers.auth_controller import router as auth_router
from controllers.guest import router as guest_router
from controllers.restaurant_controller import router as restaurant_router
from controllers.table_controller import router as table_router
from models.guest_session import GuestSession
from models.qr_code import QRCode
from models.restaurant import Restaurant
from models.restaurant_table import RestaurantTable
from models.user import User
from utils.dependencies import get_current_user as dependencies_get_current_user, oauth2_scheme
from utils.jwt import decode_token
from utils.security import hash_password

test_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
test_db_path = test_db_file.name
test_db_file.close()

test_engine = create_engine(
    f"sqlite:///{test_db_path}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _create_required_tables():
    for table_name in [
        "app_user",
        "restaurants",
        "restaurant_table",
        "qr_code",
        "guest_session",
    ]:
        Base.metadata.tables[table_name].create(bind=test_engine, checkfirst=True)


def _drop_required_tables():
    for table_name in [
        "guest_session",
        "qr_code",
        "restaurant_table",
        "restaurants",
        "app_user",
    ]:
        if table_name in Base.metadata.tables:
            Base.metadata.tables[table_name].drop(bind=test_engine, checkfirst=True)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(override_get_db),
):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_uuid = UUID(str(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


@pytest.fixture(scope="session")
def app():
    _create_required_tables()
    app = FastAPI(title="S2O API BVA")
    app.include_router(auth_router)
    app.include_router(restaurant_router)
    app.include_router(table_router)
    app.include_router(guest_router)
    app.dependency_overrides[database_get_db] = override_get_db
    app.dependency_overrides[session_get_db] = override_get_db
    app.dependency_overrides[dependencies_get_current_user] = override_get_current_user
    return app


@pytest.fixture(scope="function")
def db():
    session = TestingSessionLocal()
    yield session
    session.close()
    _drop_required_tables()
    _create_required_tables()


@pytest.fixture(scope="function")
def client(app, db):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def owner_user(db):
    user = User(
        id=uuid4(),
        email="owner@test.com",
        password_hash=hash_password("ValidPass123"),
        display_name="Owner User",
        role="owner",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def customer_user(db):
    user = User(
        id=uuid4(),
        email="customer@test.com",
        password_hash=hash_password("ValidPass123"),
        display_name="Customer User",
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def owner_headers(owner_user, client):
    resp = client.post(
        "/auth/login",
        json={"email": "owner@test.com", "password": "ValidPass123"},
    )
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def customer_headers(customer_user, client):
    resp = client.post(
        "/auth/login",
        json={"email": "customer@test.com", "password": "ValidPass123"},
    )
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def test_restaurant(db, owner_user):
    restaurant = Restaurant(
        id=uuid4(),
        name="Test Restaurant",
        description="Test restaurant for BVA",
        owner_id=owner_user.id,
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


@pytest.fixture
def test_table(db, test_restaurant):
    table = RestaurantTable(
        id=uuid4(),
        restaurant_id=test_restaurant.id,
        name="Table 1",
        seats=4,
        status="available",
    )
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@pytest.fixture
def test_qr_code(db, test_restaurant, test_table):
    qr = QRCode(
        id=uuid4(),
        restaurant_id=test_restaurant.id,
        table_id=test_table.id,
        code="test-qr-code-" + str(uuid4())[:8],
        type="table",
        status="active",
        image_path="/test.png",
    )
    db.add(qr)
    db.commit()
    db.refresh(qr)
    return qr


@pytest.fixture(autouse=True)
def _ensure_media_dirs():
    Path("media/restaurants").mkdir(parents=True, exist_ok=True)
    Path("media/menus").mkdir(parents=True, exist_ok=True)
    yield


def pytest_sessionfinish(session, exitstatus):
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass
