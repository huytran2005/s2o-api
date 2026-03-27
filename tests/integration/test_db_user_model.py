import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from models.user import User

FAKE_SECRET_HASH = "test-hash"


@pytest.fixture
def sqlite_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine, tables=[User.__table__])
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine, tables=[User.__table__])


def test_user_crud_round_trip(sqlite_session):
    user = User(
        id=uuid.uuid4(),
        email="db-user@example.com",
        password_hash=FAKE_SECRET_HASH,
        display_name="Database User",
        phone="0123456789",
        role="customer",
    )
    sqlite_session.add(user)
    sqlite_session.commit()

    created = sqlite_session.query(User).filter(User.email == "db-user@example.com").first()
    assert created is not None
    assert created.display_name == "Database User"

    created.display_name = "Updated User"
    sqlite_session.commit()

    updated = sqlite_session.query(User).filter(User.email == "db-user@example.com").first()
    assert updated.display_name == "Updated User"

    sqlite_session.delete(updated)
    sqlite_session.commit()

    deleted = sqlite_session.query(User).filter(User.email == "db-user@example.com").first()
    assert deleted is None
