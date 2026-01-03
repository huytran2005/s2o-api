import uuid
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.database import Base


class MenuItemReview(Base):
    __tablename__ = "menu_item_review"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    restaurant_id = Column(UUID(as_uuid=True), nullable=False)
    order_id = Column(UUID(as_uuid=True), nullable=False)
    order_line_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    menu_item_id = Column(UUID(as_uuid=True), nullable=False)

    rating = Column(Integer, nullable=False)
    comment = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
