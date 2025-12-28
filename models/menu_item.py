import uuid
from sqlalchemy import Column, String, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from db.database import Base

class MenuItem(Base):
    __tablename__ = "menu_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), nullable=False)
    category_id = Column(UUID(as_uuid=True), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Numeric, nullable=False)

    is_available = Column(Boolean, default=True)
    image_url = Column(String)
    meta = Column(JSONB)
