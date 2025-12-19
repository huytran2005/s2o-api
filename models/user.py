import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "app_user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    display_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    role = Column(String, nullable=False, default="customer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
