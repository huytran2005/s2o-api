import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base

class Tenant(Base):
    __tablename__ = "tenant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
