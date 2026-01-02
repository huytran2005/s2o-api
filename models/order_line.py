import uuid
from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base

class OrderLine(Base):
    __tablename__ = "order_line"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)

    menu_item_id = Column(UUID(as_uuid=True), nullable=False)
    item_name = Column(Text, nullable=False)

    qty = Column(Integer, nullable=False)
    unit_price = Column(Numeric, nullable=False)
    note = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="lines")
