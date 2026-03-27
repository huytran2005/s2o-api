from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from db.database import Base


class RestaurantTable(Base):
    __tablename__ = "restaurant_table"

    __table_args__ = (
        UniqueConstraint("restaurant_id", "name", name="uq_restaurant_table_name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)

    name = Column(Text, nullable=False)          # Bàn 1, VIP-01
    seats = Column(Integer, nullable=False)
    status = Column(Text, default="available")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant")
