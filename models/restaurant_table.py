import uuid
from datetime import datetime
from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base


class RestaurantTable(Base):
    __tablename__ = "restaurant_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)

    name = Column(Text, nullable=False)          # Bàn 1, Bàn 2, VIP-01
    seats = Column(Integer, nullable=False)
    status = Column(Text, default="available")   # available | occupied | inactive
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant")
