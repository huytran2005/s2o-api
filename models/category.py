import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base
class Category(Base):
    __tablename__ = "menu_category"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    icon = Column(String)
