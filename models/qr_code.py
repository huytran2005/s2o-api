import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.database import Base


class QRCode(Base):
    __tablename__ = "qr_code"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    restaurant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurants.id"),
        nullable=False
    )

    table_id = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurant_table.id"),
        nullable=False
    )

    code = Column(String, unique=True, nullable=False)
    type = Column(String, default="table")
    status = Column(String, default="active")

    image_path = Column(String, nullable=True)  # ← LƯU FILE QR

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    restaurant = relationship("Restaurant")
    table = relationship("RestaurantTable")
